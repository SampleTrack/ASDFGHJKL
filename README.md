# 🛒 E-commerce Price Tracker Bot

A powerful Telegram bot built with **Pyrogram** and **MongoDB (Motor)** to track prices on Amazon and Flipkart. It notifies users instantly when prices change.

## 🚀 Features
- **Real-time Tracking**: Background scheduler checks prices periodically.
- **Admin Dashboard**: Ban/Unban, Broadcast, Stats, Logs.
- **Multi-User**: Supports thousands of users via Async Database.
- **Deploy Ready**: Configured for Render, Heroku, or VPS.

## 🛠️ Deployment on Render

1. **Fork this repository.**
2. **Create a MongoDB Database** (MongoDB Atlas is free).
3. **Get Telegram API credentials** (my.telegram.org) and **Bot Token** (@BotFather).
4. Click the button below:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### ⚙️ Environment Variables

| Variable | Description | Example |
| :--- | :--- | :--- |
| `API_ID` | Telegram API ID | `123456` |
| `API_HASH` | Telegram API Hash | `abcdef123456` |
| `BOT_TOKEN` | Bot Token from BotFather | `123:ABC...` |
| `DB_URL` | MongoDB Connection URL | `mongodb+srv://...` |
| `DB_NAME` | Database Name | `PriceBot` |
| `ADMINS` | Admin User IDs (comma separated) | `12345, 67890` |
| `LOG_CHANNEL` | Channel ID for Logs | `-100123456789` |

## 🤖 Commands

**User Commands:**
- `/start` - Start the bot
- `/help` - Usage instructions
- `/trackings` - View tracked items

**Admin Commands:**
- `/stats` - View bot statistics
- `/broadcast` - Send message to all users (Reply to message)
- `/logs` - Get the `log.txt` file
- `/ban [id]` - Ban a user
- `/unban [id]` - Unban a user
- `/ping` - Check server latency

## 👨‍💻 Local Development

1. Clone repo: `git clone https://github.com/YourName/Repo.git`
2. Install reqs: `pip install -r requirements.txt`
3. Edit `config.py` or `.env`
4. Run: `python3 main.py`

---
*Developed by BotIO Devs*
