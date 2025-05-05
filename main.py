import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import razorpay
from pymongo import MongoClient
import time
import threading
from datetime import datetime, timedelta
import pytz
from config import *
from broadcast import register_admin_handlers
from status import register_status_handler
import threading
from dashboard import run_dashboard


bot = telebot.TeleBot(BOT_TOKEN)
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))
client = MongoClient(MONGO_URI)
db = client["subscription_bot"]
users_collection = db["users"]
paid_collection = db["paid_users"]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "N/A"
    first_name = message.from_user.first_name or "User"
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist).strftime("%d %B %Y, %I:%M %p")

    users_collection.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id, "username": username}},
        upsert=True,
    )

    image_url = "https://i.ibb.co/DPf9tr34/x.jpg"

    caption = f"""👾 *Welcome, {first_name}* 👾

🔹 *Username:* `@{username}`
🔹 *User ID:* `{user_id}`
🕒 *Accessed on:* `{current_time}`

🔐 _Next-gen access powered by AI & UPI AutoPay_

💠 Choose Your Plan:
• ₹1/week
• ₹5/month
• ₹10/year 

🛡️ Secure | 🤖 Automated | ⚡ Fast

Click below to activate your pass ⬇️"""

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🚀 Weekly | ₹1/week", callback_data="subscribe_week"))
    markup.add(InlineKeyboardButton("📅 Monthly | ₹5/month", callback_data="subscribe_month"))
    markup.add(InlineKeyboardButton("📆 Yearly | ₹10/year", callback_data="subscribe_year"))


    bot.send_photo(user_id, image_url, caption=caption, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("subscribe_"))
def handle_subscribe(call):
    user_id = call.message.chat.id
    plan_type = call.data.split("_")[1]
    plan_id = RAZORPAY_PLANS.get(plan_type)

    if not plan_id:
        bot.send_message(user_id, "❌ Invalid plan selected.")
        return

    start_at = int(time.time()) + START_TIME
    expire_by = int(time.time()) + EXPIRE_TIME

    try:
        subscription = razorpay_client.subscription.create({
            "plan_id": plan_id,
            "total_count": LOOP_PAY,
            "quantity": 1,
            "start_at": start_at,
            "expire_by": expire_by,
            "customer_notify": 1
        })

        sub_id = subscription['id']
        short_url = subscription['short_url']

        paid_collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "subscription_id": sub_id,
                "plan_id": plan_id,
                "plan_type": plan_type,
                "payment_link": short_url,
                "status": "created",
                "created_at": time.time(),
                "invite_link": None
            }},
            upsert=True
        )

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💳 Pay Now", url=short_url))
        bot.send_message(user_id, f"Click below to pay for your *{plan_type}* subscription:", reply_markup=markup, parse_mode="Markdown")

        threading.Thread(target=expire_if_unpaid, args=(user_id, sub_id)).start()

    except Exception as e:
        print(f"[Subscription Error] {e}")
        bot.send_message(user_id, "⚠️ Failed to create subscription. Try again later.")

def expire_if_unpaid(user_id, sub_id):
    time.sleep(300)
    try:
        sub = razorpay_client.subscription.fetch(sub_id)
        if sub['status'] == "created":
            razorpay_client.subscription.cancel(sub_id)
            paid_collection.update_one({"user_id": user_id}, {"$set": {"status": "cancelled"}})
            bot.send_message(user_id, "❌ Subscription expired due to non-payment.")
    except Exception as e:
        print(f"[Expire Check Error] {user_id} - {e}") 

def monitor_subscriptions():
    while True:
        users = paid_collection.find({"status": {"$in": ["created", "authenticated", "active"]}})
        for user in users:
            user_id = user["user_id"]
            try:
                sub = razorpay_client.subscription.fetch(user["subscription_id"])
                current_status = sub["status"]
                print(f"[Checking] User {user_id} - Status: {current_status}")

                if current_status in ["authenticated", "active"] and user.get("invite_link") is None:
                    expire_time = datetime.now() + timedelta(minutes=LINK_EXPIRE)
                    invite = bot.create_chat_invite_link(
                        chat_id=CHANNEL_ID,
                        member_limit=1,
                        expire_date=expire_time
                    )
                    bot.send_message(
                        user_id,
                        f"✅ Subscription active.\nNext due on {time.strftime('%d %B %Y', time.localtime(sub['current_end']))}\nInvite link (valid for 1 minute):\n{invite.invite_link}"
                    )
                    paid_collection.update_one({"user_id": user_id}, {
                        "$set": {
                            "status": current_status,
                            "next_due_on": time.strftime('%d %B %Y', time.localtime(sub["current_end"])),
                            "invite_link": invite.invite_link
                        }
                    })
                elif current_status in ["cancelled", "halted", "pending"] and user.get("status") != "banned":
                    try:
                        bot.ban_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
                        time.sleep(3)
                        bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
                        paid_collection.update_one({"user_id": user_id}, {"$set": {"status": "banned"}})
                        bot.send_message(user_id, "🚫 Removed from channel due to cancelled/unpaid subscription.")
                        print(f"[KICKED] User {user_id}")
                    except Exception as ban_error:
                        print(f"[Kick Error] {user_id} - {ban_error}")
            except Exception as e:
                print(f"[Monitor Error] {user_id} - {e}")

        time.sleep(60)

def send_due_reminders():
    while True:
        now = time.time()
        users = paid_collection.find({"status": "active", "next_due_on": {"$exists": True}})
        for user in users:
            due_date = datetime.strptime(user["next_due_on"], "%d %B %Y")
            due_ts = time.mktime(due_date.timetuple())
            if 0 < due_ts - now <= 3600: 
                try:
                    bot.send_message(user["user_id"], "⏰ Reminder: Your subscription will renew in 1 hour. Ensure your UPI AutoPay is active.")
                except Exception as e:
                    print(f"[Reminder Error] {e}")
        time.sleep(600)
        

threading.Thread(target=send_due_reminders, daemon=True).start()
       

register_admin_handlers(bot, users_collection)
register_status_handler(bot, users_collection, paid_collection)

print("Bot running...")
threading.Thread(target=monitor_subscriptions, daemon=True).start()
threading.Thread(target=run_dashboard, daemon=True).start()
bot.infinity_polling()
