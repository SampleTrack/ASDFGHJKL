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

app = Client(
    Telegram.BOT_NICKNAME,
    api_id=Telegram.API_ID,
    api_hash=Telegram.API_HASH,
    bot_token=Telegram.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

def main():
    async def startup():
        try:
            await app.send_message(Telegram.ADMIN, "Bot restarted")
            asyncio.create_task(price_check_runner(app))
        except Exception as e:
            print(f"Failed to send message: {e}")

    # Initiate logger
    logger = init_logger(app, __name__)
    print("Bot started")

    # Start the Web Server
    if Server.IS_SERVER:
        start_web_server()

    # Start Pyrogram Client
    app.start()
    app.loop.run_until_complete(startup())
    idle()
    app.stop()

if __name__ == "__main__":
    main()
