import asyncio
import datetime
import pytz
import logging
from aiohttp import web
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME, LOG_CHANNEL, PORT
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check
from plugins import web_server  # Assuming this returns a web.Application object or routes

# Initialize Logger
init_logger()

async def price_check_runner(client: Client):
    """Runs run_price_check every 5 hours (18000 seconds)."""
    logging.info("Starting Price Check Loop...")
    while True:
        try:
            # wait 10 seconds before first run to let bot settle
            await asyncio.sleep(10) 
            await run_price_check(client, manual_trigger=False)
        except Exception as e:
            logging.exception("Error in price_check_runner: %s", e)
        
        # Wait for 5 hours
        await asyncio.sleep(18000)

async def get_ist_time():
    """Helper to get current Date and Time in India."""
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%I:%M:%S %p")
    return date_str, time_str

class Bot(Client):
    def __init__(self):
        super().__init__(
            name=BOT_NAME,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=10,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        
        logging.info(f"{me.first_name} Started Successfully!")

        # 1. Send Startup Log to Channel
        if LOG_CHANNEL:
            try:
                date, time = await get_ist_time()
                await self.send_message(
                    chat_id=LOG_CHANNEL,
                    text=f"**🤖 Bot Restarted**\n\n📅 Date: `{date}`\n⏰ Time: `{time}`"
                )
            except Exception as e:
                logging.error(f"Failed to send startup log: {e}")

        # 2. Start the Web Server (for Render/Heroku/Health checks)
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        logging.info(f"Web Server initialized on port {PORT}")

        # 3. Start the Background Price Check Task
        # asyncio.create_task ensures this runs in the background without blocking the bot
        asyncio.create_task(price_check_runner(self))
        logging.info("Background tasks started.")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped.")

if __name__ == "__main__":
    bot = Bot()
    bot.run()
