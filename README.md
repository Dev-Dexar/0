# Telegram Subscription Bot

A Telegram bot integrated with Razorpay AutoPay for handling weekly, monthly, and yearly subscriptions. Includes a dashboard for status and user management.

## 🚀 Deploy on Heroku

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/pagal4209/j)


### 🧩 Features

- Telegram bot with Razorpay AutoPay
- Supports one-time, weekly, monthly, and yearly plans
- Invite-only access to private channels
- MongoDB backend
- Admin broadcast and user dashboard

### 🔧 Environment Variables

Make sure to set these in Heroku or your `.env` file:

```env
BOT_TOKEN=
RAZORPAY_KEY=
RAZORPAY_SECRET=
CHANNEL_ID=
ADMIN_ID=
MONGO_URI=
ADMIN_SECRET=
RAZORPAY_WEEK=
RAZORPAY_MONTH=
RAZORPAY_YEAR=
START_TIME=
EXPIRE_TIME=
LOOP_PAY=
LINK_EXPIRE=
