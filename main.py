import asyncio
import datetime
import pytz
from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN, BOT_NAME, ADMINS, IS_SERVER, LOG_CHANNEL
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check
from Script import script 
from server import start_server

# Initialize the Client
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
        except asyncio.CancelledError:
            # This allows the task to stop gracefully when we shut down the bot
            print("Price check runner stopped.")
            break
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
        me = await client.get_me()
        date, time = await get_ist_time()

        # Notify Admins
        for admin in ADMINS:
            try:
                await client.send_message(chat_id=admin, text=script.ADMIN_RESTART_MSG)
            except Exception:
                pass # Ignore errors if admin blocks bot

        # Log to Channel
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

async def main():
    # --- STEP 1: Server Check ---
    if IS_SERVER:
        print("Starting Web Server...")
        start_server()

    # --- STEP 2: Init Logger ---
    init_logger(app, __name__)
    print("Bot initializing...")

    # --- STEP 3: Start Telegram Client ---
    await app.start()
    
    # --- STEP 4: Start Background Task ---
    # We assign it to a variable 'task' so we can control it later
    task = asyncio.create_task(price_check_runner(app))
    
    # Send Notifications
    await send_startup_logs(app)
    print("Bot is successfully started and running.")

    # --- STEP 5: The Infinite Loop (IDLE) ---
    try:
        # This line freezes the code here. It acts like a wall.
        # Nothing below this runs until you stop the bot.
        await idle()
    
    except Exception as e:
        print(f"Bot stopped due to error: {e}")
    
    finally:
        # --- STEP 6: The Shutdown Sequence ---
        # This ONLY runs when the idle() loop is broken (Ctrl+C or Server Restart)
        print("Shutting down bot...")
        
        # A. Stop the background task gracefully
        task.cancel()
        
        # B. Stop the Telegram Client
        await app.stop()
        print("Bot Stopped. Goodbye!")

if __name__ == "__main__":
    app.run(main())
