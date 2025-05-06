import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RAZORPAY_KEY = os.getenv("RAZORPAY_KEY")
RAZORPAY_SECRET = os.getenv("RAZORPAY_SECRET")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "12345")

RAZORPAY_PLANS = {
    "week": os.getenv("RAZORPAY_WEEK", "plan_QRHMNOkp82MeWz"),
    "month": os.getenv("RAZORPAY_MONTH", "plan_QLjVbYTMyXO74d"),
    "year": os.getenv("RAZORPAY_YEAR", "plan_QLjW2npA6Lig82")
}

START_TIME = 600
EXPIRE_TIME = 600
LOOP_PAY = 12
LINK_EXPIRE = 10
