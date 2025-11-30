import asyncio
import datetime
import pytz
from pyrogram import Client, idle, compose
from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME, ADMINS, IS_SERVER, LOG_CHANNEL
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check
from Script import script # Import the text variables
from server import start_server

app = Client(
    BOT_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins"),
)

async def price_check_runner(client: Client):
    """Background task to check prices periodically."""
    print("Price check runner started...")
    while True:
        try:
            # manual_trigger=False means it runs automatically
            await run_price_check(client, manual_trigger=False)
        except Exception as e:
            print(f"Error in price checker: {e}")
        
        # Sleep for 5 hours (18000 seconds)
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
        # 1. Get Bot Info for the log
        me = await client.get_me()
        date, time = await get_ist_time()

        # 2. Notify Admins
        for admin in ADMINS:
            try:
                await client.send_message(
                    chat_id=admin, 
                    text=script.ADMIN_RESTART_MSG
                )
            except Exception as e:
                print(f"Could not send start msg to admin {admin}: {e}")

        # 3. Send formatted log to Log Channel
        if LOG_CHANNEL:
            try:
                log_text = script.STARTUP_LOG_TXT.format(
                    bot_name=me.first_name,
                    bot_username=me.username,
                    date=date,
                    time=time
                )
                await client.send_message(
                    chat_id=LOG_CHANNEL,
                    text=log_text
                )
                print("Startup log sent to channel.")
            except Exception as e:
                print(f"Failed to send log to channel: {e}")

    except Exception as e:
        print(f"Error in startup logs: {e}")

async def main():
    # 1. Start the Web Server if on Server
    if IS_SERVER:
        print("Starting Web Server...")
        start_server()

    # 2. Initialize Logger
    init_logger(app, __name__)
    print("Bot initializing...")

    # 3. Start the Bot Client
    await app.start()
    
    # 4. Run Startup Tasks (Logs & Background runner)
    # We use create_task for the loop so it doesn't block the main thread
    asyncio.create_task(price_check_runner(app))
    
    # Send the notifications
    await send_startup_logs(app)
    
    print("Bot is now Idle and Running.")
    
    # 5. Idle (Keep bot running)
    await idle()
    
    # 6. Stop
    await app.stop()

if __name__ == "__main__":
    # This automatically creates the event loop and runs main()
    app.run(main())
    
    
