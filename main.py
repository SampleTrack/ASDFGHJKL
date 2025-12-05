import logging
import asyncio
from pyrogram import Client, idle
from flask import Flask
from threading import Thread
from config import Config
from plugins.scheduler import start_scheduler

# Configure Logging to file
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("bot_logs.txt"),
        logging.StreamHandler()
    ]
)

# Initialize Flask
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running Successfully!", 200

def run_web():
    web_app.run(host="0.0.0.0", port=Config.PORT)

# Initialize Pyrogram Client
app = Client(
    "PriceTrackerBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def start_bot():
    print("--- Starting Bot ---")
    await app.start()
    
    # Start the price check scheduler
    asyncio.create_task(start_scheduler(app))
    
    print("--- Bot Started ---")
    await idle()
    await app.stop()

if __name__ == "__main__":
    # Run Flask in a separate thread
    flask_thread = Thread(target=run_web)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run Pyrogram
    app.run(start_bot())
