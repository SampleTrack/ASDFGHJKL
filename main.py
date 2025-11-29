# main.py
import asyncio
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME, ADMINS, IS_SERVER
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check

# Import the server function we just created
from server import start_server 

app = Client(
    BOT_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
)

async def price_check_runner(client: Client):
    print("Price check runner started...")
    while True:
        try:
            await run_price_check(client, manual_trigger=False)
        except Exception as e:
            print(f"Error in price checker: {e}")
        # Sleep for 5 hours (18000 seconds)
        await asyncio.sleep(18000)  

async def startup():
    try:
        # Send a message to admins so you know it restarted
        for admin in ADMINS:
            try:
                await app.send_message(admin, "Bot restarted and is online!")
            except Exception:
                pass
        
        # Start the background task
        asyncio.create_task(price_check_runner(app))
    except Exception as e:
        print(f"Failed to run startup tasks: {e}")

if __name__ == "__main__":
    # 1. Initiate Logger
    logger = init_logger(app, __name__)
    print("Bot initializing...")

    # 2. Start the Web Server (Keep Alive) if on Server
    if IS_SERVER:
        print("Starting Web Server...")
        start_server()

    # 3. Start the Bot
    app.start()
    
    # 4. Run startup tasks (background runner)
    app.loop.run_until_complete(startup())
    
    print("Bot is now Idle and Running.")
    idle()
    app.stop()
