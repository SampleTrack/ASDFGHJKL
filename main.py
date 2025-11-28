import os
import asyncio
import threading
import logging
from pyrogram import Client, idle
from flask import Flask
from config import Telegram, Server
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check

# Initialize Flask
web_app = Flask(__name__)

@web_app.route("/")
def hello_world():
    return "Hello, World! Bot is running."

async def price_check_runner(client: Client):
    """
    Background task to run price checks every 5 hours (18000 seconds).
    Includes error handling to ensure the loop doesn't die on a single error.
    """
    print("Background price check task started.")
    while True:
        try:
            # Run the check
            await run_price_check(client, manual_trigger=False)
        except Exception as e:
            logging.error(f"Error in price_check_runner: {e}")
        
        # Sleep for 5 hours
        await asyncio.sleep(18000)

def run_flask():
    """
    Runs the Flask server in a separate thread.
    Crucial: Uses os.environ.get("PORT") to satisfy cloud health checks.
    """
    try:
        # Disable annoying Werkzeug logs
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        web_app.logger.setLevel(logging.ERROR)

        # Get the PORT from environment variables (Required for Cloud Hosting)
        # Default to 7860 if no variable is found
        http_port = int(os.environ.get("PORT", 8080))
        
        print(f"--- Flask Server starting on Port {http_port} ---")
        web_app.run(host="0.0.0.0", port=http_port)
    except Exception as e:
        logging.exception(f"Flask server failed to start: {e}")

# Initialize Pyrogram Client
app = Client(
    Telegram.BOT_NICKNAME,
    api_id=Telegram.API_ID,
    api_hash=Telegram.API_HASH,
    bot_token=Telegram.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

def main():
    # 1. Initialize Logger
    init_logger(app, __name__)
    print("Logger Initialized.")

    # 2. Start Flask Server (If enabled in Config)
    if Server.IS_SERVER:
        print("Starting Flask Thread...")
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
    else:
        print("Server.IS_SERVER is False. Flask will NOT start.")

    # 3. Start the Pyrogram Client
    print("Starting Telegram Bot Client...")
    app.start()

    # 4. Perform Startup Actions (Send Msg & Start Background Task)
    try:
        me = app.get_me()
        print(f"Bot started as {me.first_name} (@{me.username})")
        
        # Send restart message
        try:
            app.send_message(Telegram.ADMIN, f"Bot Restarted: @{me.username}")
        except Exception as e:
            print(f"Failed to send startup message: {e}")

        # Start the background task loop
        # We use app.loop.create_task to ensure it runs on the same loop as the bot
        app.loop.create_task(price_check_runner(app))
        
    except Exception as e:
        print(f"Startup error: {e}")

    # 5. Keep the bot running
    print("Bot is idling...")
    idle()
    
    # 6. Stop
    app.stop()
    print("Bot stopped.")

if __name__ == "__main__":
    main()
