import os
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database import db
import asyncio

@Client.on_message(filters.command("logs") & filters.user(Config.ADMIN_ID))
async def logs_handler(client, message: Message):
    """Sends the bot_logs.txt file to the admin"""
    if os.path.exists("bot_logs.txt"):
        await message.reply_document("bot_logs.txt", caption="📄 **System Logs**")
    else:
        await message.reply("❌ No log file found.")

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN_ID))
async def broadcast_handler(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("⚠️ **Reply to a message to broadcast.**")
    
    status = await message.reply("⏳ **Broadcasting...**")
    users = db.get_all_users()
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            await message.reply_to_message.copy(user['user_id'])
            success += 1
            await asyncio.sleep(0.5) # Avoid FloodWait
        except Exception:
            failed += 1
            
    await status.edit(f"✅ **Broadcast Complete**\n\nSent: `{success}`\nFailed: `{failed}`")
