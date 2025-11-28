import asyncio
import threading
import logging
import sys
from pyrogram import Client, idle
from flask import Flask

# Import from your helper files
from config import Telegram, Server
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check

# --- Flask Setup ---
web_app = Flask(__name__)

@web_app.route("/")
def hello_world():
    return "Hello, World! Bot is running."

def run_flask():
    """Runs the Flask server in a separate thread."""
    try:
        # Suppress Flask dev server logs
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        web_app.logger.setLevel(logging.ERROR)
        
        # Use port from Config
        web_app.run(host="0.0.0.0", port=Server.PORT)
    except Exception as e:
        logging.error(f"Flask server failed to start: {e}")

# --- Pyrogram Setup ---
app = Client(
    Telegram.BOT_NICKNAME,
    api_id=Telegram.API_ID,
    api_hash=Telegram.API_HASH,
    bot_token=Telegram.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

# --- Background Task ---
async def price_check_runner(client: Client):
    """Runs the price check loop in the background continuously."""
    logger = logging.getLogger(__name__)
    logger.info("Price Check Background Task Started.")
    
    while True:
        try:
            # Run the check
            await run_price_check(client, manual_trigger=False)
        except Exception as e:
            logger.error(f"CRITICAL ERROR in price_check_runner: {e}", exc_info=True)
        
        # Wait for 5 hours (18000 seconds) before next run
        # We wait here regardless of success or failure to prevent spam-looping on error
        await asyncio.sleep(18000)

async def main():
    """Main async entry point."""
    
    # 1. Initialize Logger
    init_logger(app, __name__)
    logger = logging.getLogger(__name__)

    # 2. Start Web Server (if enabled)
    if Server.IS_SERVER:
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info(f"Flask server started on port {Server.PORT}")

    # 3. Start Pyrogram Client
    logger.info("Starting Telegram Bot...")
    await app.start()
    
    # 4. Get Bot Info & Notify Admin
    me = await app.get_me()
    logger.info(f"Bot started as {me.first_name} (@{me.username})")
    
    try:
        await app.send_message(Telegram.ADMIN, f"🤖 **{me.first_name}** has restarted successfully!")
    except Exception as e:
        logger.warning(f"Could not send startup message to Admin: {e}")

    # 5. Start Background Task
    # We use create_task to run it concurrently with the bot's idle loop
    checker_task = asyncio.create_task(price_check_runner(app))

    # 6. Idle (Keep bot running)
    await idle()

    # 7. Graceful Shutdown
    logger.info("Stopping Bot...")
    await app.stop()
    checker_task.cancel() # Cancel the background task
    logger.info("Bot Stopped.")

if __name__ == "__main__":
    try:
        # Uses the default event loop policy
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal Error: {e}")
