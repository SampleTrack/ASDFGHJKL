# 🛒 Telegram E-Commerce Price Tracker Bot

A powerful Telegram bot to track prices of products on **Amazon** and **Flipkart**. It notifies users instantly when the price changes.

## ✨ Features
- 📉 **Auto Price Tracking:** Checks prices every 4 hours.
- 🔔 **Instant Notifications:** Alerts when price drops or increases.
- 📊 **User Dashboard:** View and manage tracked products.
- 🛠 **Admin Tools:** Broadcast messages, view system logs.
- ☁️ **Deploy Ready:** Ready for Render, Heroku, or VPS.

---

## 🚀 Deploy to Render (Easiest Method)

1. Click the button below.
2. Fill in the **Environment Variables** (see below).
3. Click **Create Web Service**.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

---

## ⚙️ Environment Variables (Config)

You must set these variables in your deployment settings:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `API_ID` | Your Telegram API ID | `123456` |
| `API_HASH` | Your Telegram API Hash | `abcdef123456...` |
| `BOT_TOKEN` | Your Bot Token from @BotFather | `12345:ABCDE...` |
| `MONGO_URI` | MongoDB Connection URL | `mongodb+srv://...` |
| `ADMIN_ID` | Your Telegram User ID (for admin cmds) | `987654321` |
| `LOG_CHANNEL_ID` | Channel ID for Logs (starts with -100) | `-100123456789` |

---

## 🛠 Commands

### User Commands
- `/start` - Check if bot is alive.
- `/help` - Show help menu.
- `/my_trackings` - Manage your tracked products.
- `/ping` - Check latency.
- `/suggest [text]` - Send a suggestion to the developer.

### Admin Commands
- `/logs` - Get the `bot_logs.txt` file (Error debugging).
- `/broadcast` - Reply to a message to send it to all users.

---

## 💻 Local Installation

1. **Clone the Repo:**
   ```bash
   git clone [https://github.com/YourUsername/PriceTrackerBot.git](https://github.com/YourUsername/PriceTrackerBot.git)
   cd PriceTrackerBot
