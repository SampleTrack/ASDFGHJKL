import asyncio
import datetime
import pytz
import logging  # FIX: Added logging
from aiohttp import web  # FIX: Added aiohttp web
from pyrogram import Client, idle
# FIX: Added PORT to imports
from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME, ADMINS, IS_SERVER, LOG_CHANNEL, PORT
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check
from Script import script 
from plugins import web_server


async def price_check_runner(client: Client):
    while True:
        # Pass the client to the checker
        await run_price_check(client, manual_trigger=False)
        await asyncio.sleep(18000) 
        
async def get_ist_time():
    """Helper to get current Date and Time in India."""
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(ist)
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%I:%M:%S %p")
    return date_str, time_str

async def send_startup_logs(client: Client):
    """Sends logs to Admins and the Log Channel."""
    try:
        me = await client.get_me()
        date, time = await get_ist_time()

        for admin in ADMINS:
            try:
                await client.send_message(chat_id=admin, text=script.ADMIN_RESTART_MSG)
            except Exception:
                pass 

        if LOG_CHANNEL:
            try:
                log_text = script.STARTUP_LOG_TXT.format(
                    bot_name=me.first_name,
                    bot_username=me.username,
                    date=date,
                    time=time
                )
                await client.send_message(chat_id=LOG_CHANNEL, text=log_text)
            except Exception as e:
                print(f"Failed to send log to channel: {e}")

    except Exception as e:
        print(f"Error in startup logs: {e}")

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
        # FIX: Must call super().start() to connect to Telegram
        await super().start()
        print("Bot Started via Pyrogram")

        # FIX: Pass 'self' (the client) to the logs function
        await send_startup_logs(self)

        # Web Server Setup
        # Renamed variable to 'runner' to avoid confusion with 'app'
        runner = web.AppRunner(await web_server())
        await runner.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(runner, bind_address, PORT).start()
        print(f"Web Server Running on Port {PORT}")

        # FIX: Pass 'self' (the client) to the background task, NOT the web runner
        asyncio.create_task(price_check_runner(self))
        
    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")
    
if __name__ == "__main__":
    app = Bot()
    app.run()
