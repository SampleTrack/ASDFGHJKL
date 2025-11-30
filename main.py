import asyncio
import datetime
import pytz
import logging
from aiohttp import web
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME, ADMINS, IS_SERVER, LOG_CHANNEL, PORT
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check
from Script import script
from plugins import web_server  # assumed to be an async function returning aiohttp.web.Application


async def price_check_runner(client: Client):
    """Runs run_price_check every 5 hours (18000 seconds)."""
    while True:
        try:
            await run_price_check(client, manual_trigger=False)
        except Exception as e:
            logging.exception("Error in price_check_runner: %s", e)
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
            plugins=dict(root="plugins"),
        )

    async def start(self):
        # call parent's start first
        await super().start()
        logging.info("Bot Started via Pyrogram")
        # initialize logger (if your helper sets up handlers)
        try:
            init_logger()
        except Exception:
            logging.exception("init_logger failed, continuing without custom logger")

        try:
            # use self (not a stray 'client' name)
            me = await self.get_me()
            date, time = await get_ist_time()

            # notify admins
            for admin in ADMINS or []:
                try:
                    await self.send_message(chat_id=admin, text=script.ADMIN_RESTART_MSG)
                except Exception:
                    logging.exception("Failed to notify admin %s", admin)

            # send startup log to channel if available
            if LOG_CHANNEL:
                try:
                    log_text = script.STARTUP_LOG_TXT.format(
                        bot_name=getattr(me, "first_name", BOT_NAME),
                        bot_username=getattr(me, "username", ""),
                        date=date,
                        time=time,
                    )
                    await self.send_message(chat_id=LOG_CHANNEL, text=log_text)
                except Exception:
                    logging.exception("Failed to send startup log to LOG_CHANNEL")

        except Exception:
            logging.exception("Error while running startup notifications")

        # Start web server (if provided) and price checker runner
        try:
            # web_server is assumed to be async and to return aiohttp.web.Application
            if callable(web_server):
                web_app = await web_server()
                runner = web.AppRunner(web_app)
                await runner.setup()
                bind_address = "0.0.0.0"
                site = web.TCPSite(runner, bind_address, PORT)
                await site.start()
                logging.info("Web Server Running on Port %s", PORT)
            else:
                logging.warning("web_server is not callable; skipping web server setup")
        except Exception:
            logging.exception("Failed to start web server")

        # start background price checker
        try:
            asyncio.create_task(price_check_runner(self))
            logging.info("Price check runner started")
        except Exception:
            logging.exception("Failed to create price check task")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")


if __name__ == "__main__":
    # Optional: basic logging config if you don't have a logging setup elsewhere
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    app = Bot()
    app.run()  # this blocks and handles start/stop lifecycle
