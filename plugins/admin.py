import os
import time
import shutil
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from config import Config
from Script import Script
from helper.database import db

@Client.on_message(filters.command("stats") & filters.user(Config.ADMINS))
async def stats_handler(client, message):
    msg = await message.reply("Calculating...")
    
    total_users = await db.total_users_count()
    today_users = await db.get_daily_users()
    total_products = await db.products.count_documents({})
    
    # Disk Usage
    total, used, free = shutil.disk_usage(".")
    total = f"{total / (1024.0 ** 3):.2f} GB"
    used = f"{used / (1024.0 ** 3):.2f} GB"
    free = f"{free / (1024.0 ** 3):.2f} GB"
    storage = f"Used: {used} / Free: {free}"
    
    text = Script.STATS_TXT.format(
        users=total_users,
        today=today_users,
        products=total_products,
        storage=storage
    )
    await msg.edit(text)

@Client.on_message(filters.command("ping"))
async def ping_handler(client, message):
    start = time.time()
    msg = await message.reply("Pong!")
    end = time.time()
    await msg.edit(f"🏓 Pong! Latency: `{round((end - start) * 1000)}ms`")

@Client.on_message(filters.command("logs") & filters.user(Config.ADMINS))
async def log_handler(client, message):
    """
    Sends a text file containing ONLY Errors and Warnings.
    Ignores standard INFO logs.
    """
    if not os.path.exists("log.txt"):
        return await message.reply("❌ No log file found.")

    status = await message.reply("🔍 **Scanning logs for errors...**")

    error_lines = []
    
    # Read the log file and filter out INFO lines
    with open("log.txt", "r", encoding="utf-8") as f:
        for line in f:
            # We keep lines that are NOT 'INFO'
            # We also strictly look for ERROR, WARNING, CRITICAL, or Python Tracebacks
            if any(x in line for x in ["ERROR", "WARNING", "CRITICAL", "Traceback", "Exception"]):
                error_lines.append(line)
            # We also keep indented lines because they usually belong to a stack trace
            elif line.startswith("  ") or line.startswith("\t"):
                 error_lines.append(line)

    if not error_lines:
        await status.edit("✅ **System Healthy:** No errors or bugs found in the logs.")
        return

    # Write the filtered errors to a temporary file
    temp_file = "bugs.txt"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.writelines(error_lines)

    try:
        await message.reply_document(
            document=temp_file,
            caption=f"🐞 **Error Log Report**\nFound `{len(error_lines)}` error lines."
        )
    except Exception as e:
        await message.reply(f"Failed to send logs: {e}")
    finally:
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
        await status.delete()

@Client.on_message(filters.command("ban") & filters.user(Config.ADMINS))
async def ban_handler(client, message):
    if len(message.command) != 2:
        return await message.reply("Usage: /ban [user_id]")
    try:
        user_id = int(message.command[1])
        await db.ban_user(user_id)
        await message.reply(f"User {user_id} has been Banned. 🚫")
    except Exception as e:
        await message.reply(f"Error: {e}")

@Client.on_message(filters.command("unban") & filters.user(Config.ADMINS))
async def unban_handler(client, message):
    if len(message.command) != 2:
        return await message.reply("Usage: /unban [user_id]")
    try:
        user_id = int(message.command[1])
        await db.unban_user(user_id)
        await message.reply(f"User {user_id} has been Unbanned. ✅")
    except Exception as e:
        await message.reply(f"Error: {e}")

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMINS))
async def broadcast_handler(client, message):
    if not message.reply_to_message:
        return await message.reply("Reply to a message to broadcast.")
    
    msg = await message.reply("Broadcast started...")
    users = await db.get_all_users()
    success = 0
    failed = 0
    
    async for user in users:
        try:
            await message.reply_to_message.copy(user['user_id'])
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(user['user_id'])
            success += 1
        except Exception:
            failed += 1
            
    await msg.edit(f"**Broadcast Complete**\n✅ Success: {success}\n❌ Failed: {failed}")
