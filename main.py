import asyncio
import threading
import logging
from pyrogram import Client, idle
from flask import Flask
from config import Telegram, Server
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check

# --- Flask Setup ---
web_app = Flask(__name__)

@web_app.route("/")
def hello_world():
    return "Hello, World!"

def run_flask():
    try:
        # Reduce Flask logging noise
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        web_app.logger.setLevel(logging.ERROR)
        web_app.run(host="0.0.0.0", port=7860)
    except Exception:
        logging.exception("Flask server crashed!")

# --- Background Task ---
async def price_check_runner(client: Client):
    """
    Runs the price check loop. 
    Includes error handling to prevent the loop from dying on a single error.
    """
    while True:
        try:
            # We wrap this in try/except so if one check fails, the loop continues
            await run_price_check(client, manual_trigger=False)
        except Exception as e:
            logging.error(f"Error in price_check_runner: {e}")
        
        # Sleep for 5 hours (18000 seconds)
        await asyncio.sleep(18000)

# --- Pyrogram Client Setup ---
app = Client(
    Telegram.BOT_NICKNAME,
    api_id=Telegram.API_ID,
    api_hash=Telegram.API_HASH,
    bot_token=Telegram.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

# --- Main Execution ---
def main():
    # 1. Initiate Logger
    init_logger(app, __name__)
    print("Bot starting...")

    # 2. Start Flask Server (Background Thread)
    if Server.IS_SERVER:
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

    # 3. Start Pyrogram Client
    app.start()
    
    # 4. Get the running loop from the app
    loop = asyncio.get_event_loop()

    # 5. Send Startup Message (Non-blocking)
    async def send_startup_msg():
        try:
            await app.send_message(Telegram.ADMIN, "Bot restarted")
        except Exception as e:
            logging.error(f"Failed to send startup message: {e}")

    # Schedule startup tasks on the event loop
    loop.create_task(send_startup_msg())
    loop.create_task(price_check_runner(app))

    print("Bot started and idle.")
    
    # 6. Idle (Keep bot running)
    idle()
    
    # 7. Stop properly on exit
    app.stop()

if __name__ == "__main__":
    main()
