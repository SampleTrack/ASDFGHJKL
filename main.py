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
    return "Hello, World!"

def run_flask():
    try:
        # Suppress Flask dev server logs
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        web_app.logger.setLevel(logging.ERROR)
        web_app.run(host="0.0.0.0", port=7860)
    except Exception:
        logging.exception("Flask server crashed!")

# Initialize Pyrogram Client
app = Client(
    Telegram.BOT_NICKNAME,
    api_id=Telegram.API_ID,
    api_hash=Telegram.API_HASH,
    bot_token=Telegram.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

async def price_check_runner(client: Client):
    """Background task to run price checks periodically."""
    print("✅ Price check background task started.")
    while True:
        try:
            # Run the check
            await run_price_check(client, manual_trigger=False)
        except Exception as e:
            logging.error(f"Error in price_check_runner: {e}", exc_info=True)
        
        # Wait for 5 hours (18000 seconds) before next run
        await asyncio.sleep(18000)

async def main():
    """Main async entry point."""
    
    # 1. Initialize Logger
    # We do this here to ensure the loop is ready if the logger needs it
    logger = init_logger(app, __name__)
    
    # 2. Start Flask in a separate thread (if enabled)
    if Server.IS_SERVER:
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        print("✅ Flask server started.")

    # 3. Start Pyrogram Client
    await app.start()
    print("✅ Bot started.")

    # 4. Perform Startup Actions
    try:
        await app.send_message(Telegram.ADMIN, "🤖 Bot restarted and ready!")
    except Exception as e:
        logger.error(f"Failed to send startup message: {e}")

    # 5. Start Background Tasks
    # We use asyncio.create_task so it runs concurrently with idle()
    asyncio.create_task(price_check_runner(app))

    # 6. Keep the bot running
    await idle()
    
    # 7. Stop properly on exit
    await app.stop()
    print("🛑 Bot stopped.")

if __name__ == "__main__":
    # app.run() automatically manages the loop and handles Ctrl+C
    app.run(main())
