from aiohttp import web
from plugins import web_server
from typing import Union, Optional, AsyncGenerator
import asyncio
from pyrogram import Client, idle
from config import Telegram, Server
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check

# Import the server starter
from server import start_web_server

async def price_check_runner(client: Client):
    while True:
        await run_price_check(client, manual_trigger=False)
        await asyncio.sleep(18000)

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=Telegram.BOT_NICKNAME,
            api_id=Telegram.API_ID,
            api_hash=Telegram.API_HASH,
            bot_token=Telegram.BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        try:
            await app.send_message(Telegram.ADMIN, "Bot restarted")
            asyncio.create_task(price_check_runner(app))
        except Exception as e:
            print(f"Failed to send message: {e}")
            
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, "8080").start()


app = Bot()
app.run()
