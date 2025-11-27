import asyncio
import threading
import logging
from pyrogram import Client, idle
from flask import Flask
from config import Telegram, Server
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check


web_app = Flask(__name__)


@web_app.route("/")
def hello_world():
    return "Hello, World!"


async def price_check_runner(client: Client):
    while True:
        await run_price_check(client, manual_trigger=False)
        await asyncio.sleep(18000)  


def run_flask():
    try:
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.ERROR)
        web_app.logger.setLevel(logging.ERROR)
        web_app.run(host="0.0.0.0", port=7860)
    except Exception:
        logging.exception("Flask server crashed!")


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
            # start background task after bot is up
            asyncio.create_task(price_check_runner(app))
        except Exception as e:
            print(f"Failed to send message: {e}")

    # initiate logger
    logger = init_logger(app, __name__)
    print("Bot started")

    if Server.IS_SERVER:
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

    app.start()
    app.loop.run_until_complete(startup())
    idle()
    app.stop()


if __name__ == "__main__":
    main()
