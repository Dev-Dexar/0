import time
from telebot import TeleBot
from pymongo.collection import Collection
from telebot.types import Message
from config import *
def register_admin_handlers(bot: TeleBot, users_collection: Collection):
    @bot.message_handler(commands=["broadcast"])
    def handle_broadcast(message: Message):
        if message.from_user.id != ADMIN_ID:
            return bot.reply_to(message, "You do not have permission to broadcast.")
        last_message = message.reply_to_message 
        if not last_message:
            return bot.reply_to(message, "You need to reply to a message to broadcast it.")
        success_count = 0
        fail_count = 0
        for user in users_collection.find():
            try:
                if last_message.content_type == "text":
                    bot.send_message(user["user_id"], last_message.text)
                elif last_message.content_type == "sticker":
                    bot.send_sticker(user["user_id"], last_message.sticker.file_id)
                elif last_message.content_type == "photo":
                    bot.send_photo(user["user_id"], last_message.photo[-1].file_id)
                elif last_message.content_type == "video":
                    bot.send_video(user["user_id"], last_message.video.file_id)
                success_count += 1
                time.sleep(2.5)
            except Exception as e:
                fail_count += 1
                print(f"Failed to send to user {user['user_id']}: {e}")
                pass
        bot.reply_to(message, f"Broadcast complete!\n"
                              f"Messages sent successfully: {success_count}\n"
                              f"Messages failed: {fail_count}")
