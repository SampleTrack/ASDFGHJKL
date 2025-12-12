import sys
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Telegram

# --- Helper Filter ---
# This ensures only the Admin defined in config.py can use these commands
async def is_admin_check(_, __, message: Message):
    if not Telegram.ADMIN: 
        return False
    return message.from_user.id == Telegram.ADMIN

admin_only = filters.create(is_admin_check)

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

# --- /logs Command ---
# (Optional) Retreives the price checker log file if it exists
@Client.on_message(filters.command("logs") & admin_only)
async def get_logs_cmd(client: Client, message: Message):
    log_path = os.path.join("logs", "price_check.log")
    
    if os.path.exists(log_path):
        await message.reply_document(
            document=log_path,
            caption="📂 **Here are the latest price check logs.**"
        )
    else:
        await message.reply("❌ **No log file found.**\nRun /check first to generate logs.")
