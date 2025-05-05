from telebot import TeleBot
from pymongo.collection import Collection
from telebot.types import Message
from config import *
def register_status_handler(bot: TeleBot, users_collection: Collection, paid_collection: Collection):
    @bot.message_handler(commands=["status"])
    def handle_status(message: Message):
        if message.from_user.id != ADMIN_ID:
            return
        total = users_collection.count_documents({})
        active = paid_collection.count_documents({"status": "active"})
        bot.reply_to(message, f"📊 *Bot Status:*\n\n👥 Total Users: `{total}`\n✅ Active Subs: `{active}`", parse_mode="Markdown")
