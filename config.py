import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("7597274168:AAEpMjinTuta78O2YmGc1YJSv5aFxZO7GzE")
RAZORPAY_KEY = os.getenv("rzp_live_Kfvz8iobE8iUZc")
RAZORPAY_SECRET = os.getenv("bcPhJQ2pHTaaF94FhWCEl6eD")
CHANNEL_ID = int(os.getenv("-1002755139288"))
ADMIN_ID = int(os.getenv("7209883949"))
MONGO_URI = os.getenv("mongodb+srv://Sinchu:Sinchu@sinchu.qwijj.mongodb.net/?retryWrites=true&w=majority&appName=Sinchu")
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "12345")

RAZORPAY_PLANS = {
    "week": os.getenv("RAZORPAY_WEEK", "plan_QUqJ2XHZz1CQyM"),
    "month": os.getenv("RAZORPAY_MONTH", "plan_QLjVbYTMyXO74d"),
    "year": os.getenv("RAZORPAY_YEAR", "plan_QLjW2npA6Lig82")
}

START_TIME = 600
EXPIRE_TIME = 600
LOOP_PAY = 12
LINK_EXPIRE = 10
