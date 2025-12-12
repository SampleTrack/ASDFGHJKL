import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Telegram

# Filter to ensure only Admin uses these commands
async def is_admin_check(_, __, message: Message):
    if not Telegram.ADMIN: 
        return False
    return message.from_user.id == Telegram.ADMIN

admin_only = filters.create(is_admin_check)

@Client.on_message(filters.command("log") & admin_only)
async def send_logs(client: Client, message: Message):
    """Sends the error log file and price check log file."""
    
    # 1. Define file paths
    error_log = "logs/error.log"
    tracker_log = "logs/price_check.log"
    
    sent = False

    # 2. Check and send Error Log
    if os.path.exists(error_log) and os.path.getsize(error_log) > 0:
        await message.reply_document(
            document=error_log,
            caption="🐞 **System Error Log**\nContains bugs and crashes."
        )
        sent = True
    
    # 3. Check and send Price Tracker Log
    if os.path.exists(tracker_log) and os.path.getsize(tracker_log) > 0:
        await message.reply_document(
            document=tracker_log,
            caption="📉 **Price Checker Log**\nDetails from the last price check run."
        )
        sent = True

    # 4. If no files found
    if not sent:
        await message.reply_text("✅ **No logs found.**\nThis means no errors have been recorded yet!")
        
        
# --- /ping Command ---
# Checks the bot's response speed (latency)
@Client.on_message(filters.command("ping") & admin_only)
async def ping_cmd(client: Client, message: Message):
    start_time = time.time()
    status_msg = await message.reply("🏓 Pong!")
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000)
    await status_msg.edit(f"🏓 **Pong!**\nLatency: `{latency}ms`")

# --- /restart Command ---
# Restarts the bot script. Useful after applying bug fixes.
@Client.on_message(filters.command("restart") & admin_only)
async def restart_cmd(client: Client, message: Message):
    await message.reply("🔄 **Restarting Bot...**\nPlease wait 10-15 seconds.")
    
    # Restarts the current script using the same python interpreter
    os.execl(sys.executable, sys.executable, "main.py")
