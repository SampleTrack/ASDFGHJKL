import asyncio
import logging
from aiohttp import web
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, PORT

# Import local modules
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check
from plugins import web_server

# 1. Initialize the Pyrogram Client
# We define plugins=dict(root="plugins") so Pyrogram loads any future handlers in that folder
Bot = Client(
    "PriceCheckBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

# 2. Initialize the Logger
# We pass the 'Bot' instance so the logger can send error reports to Telegram
logger = init_logger(Bot)


async def price_check_runner(client: Client):
    """
    Runs run_price_check every 5 hours (18000 seconds).
    Started as a background task in the main loop.
    """
    logger.info("Starting Price Check Loop...")
    
    # Wait 10 seconds before first run to let the bot connect and settle
    await asyncio.sleep(10)
    
    while True:
        try:
            await run_price_check(client, manual_trigger=False)
        except Exception as e:
            logger.exception(f"Error in price_check_runner: {e}")
        
        # Wait for 5 hours (18000 seconds)
        await asyncio.sleep(18000)


async def start_bot():
    """
    Main entry point to start the Bot, Web Server, and Background Tasks.
    """
    try:
        # --- A. Start the Telegram Bot ---
        await Bot.start()
        me = await Bot.get_me()
        logger.info(f"Bot Started as @{me.username}")

        # --- B. Start the Aiohttp Web Server ---
        # This uses the factory function from plugins/__init__.py
        app = await web_server()
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Binds to 0.0.0.0 and the PORT from config
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        logger.info(f"Web server operational on port {PORT}")

        # --- C. Start Background Tasks ---
        # Create a non-blocking task for the price checker
        asyncio.create_task(price_check_runner(Bot))

        # --- D. Keep the process alive ---
        await idle()

    except Exception as e:
        logger.error(f"Critical error during startup: {e}")
    finally:
        # --- E. Cleanup on Stop ---
        await Bot.stop()
        logger.info("Bot Stopped.")

if __name__ == "__main__":
    # Run the async loop
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"Fatal error in event loop: {e}")
