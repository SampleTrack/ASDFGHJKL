import os
import shutil
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from config import Config
from Script import Script
from helper.database import db

# --- EXAMPLE 2: DETAILED ADMIN STATS ---
@Client.on_message(filters.command("stats") & filters.user(Config.ADMINS))
async def stats_handler(client, message):
    msg = await message.reply("🔄 **Calculating Advanced Stats...**", quote=True)
    start_t = time.time()

    total_users = await db.total_users_count()
    total_products = await db.products.count_documents({})
    
    # Source Breakdown
    sources_data = await db.count_products_by_source()
    source_txt = ""
    for s in sources_data:
        source_txt += f"  - **{s['_id']}**: {s['count']} products\n"
    if not source_txt: source_txt = "  - None"

    # Top Users
    top_users_data = await db.get_top_users(limit=10)
    top_users_txt = ""
    for i, u in enumerate(top_users_data, 1):
        top_users_txt += f"  {i}. **ID:** `{u['user_id']}` - {u['tracking_count']} trackings\n"
    if not top_users_txt: top_users_txt = "  - None"

    end_t = time.time()
    taken = round(end_t - start_t, 2)

    text = Script.STATS_TXT.format(
        users=total_users,
        trackings=total_products,
        sources=source_txt,
        top_users=top_users_txt,
        time=taken
    )
    await msg.edit(text)

# --- EXAMPLE 1: LAST CHECK STATUS ---
@Client.on_message(filters.command("check_status") & filters.user(Config.ADMINS))
async def check_status_handler(client, message):
    stats_obj = Config.LAST_CHECK_STATS
    
    if not stats_obj or stats_obj["data"] is None:
        return await message.reply("⚠️ No price checks have run yet. Wait for the loop.", quote=True)

    data = stats_obj["data"]
    perf = stats_obj["perf"]

    plat_txt = ""
    for k, v in data["platforms"].items():
        plat_txt += f"🌐 {k}: {v['checked']} checked, {v['drops']} drops.\n"

    # Get live counts for dynamic fields
    total_active_users = await db.get_active_trackings_count() 
    users_with_trackings = await db.get_users_with_trackings_count()

    text = Script.STATUS_TXT.format(
        date=stats_obj["date"],
        checked=data["checked"],
        active_tr=total_active_users,
        user_tr=users_with_trackings,
        inc=data["inc"],
        dec=data["dec"],
        platforms=plat_txt,
        uniq_users=data["unique_users_notified"],
        sent=data["sent"],
        failed=data["failed"],
        errors=data["errors"],
        avg_time=perf["avg"],
        total_time=perf["total"]
    )
    await message.reply(text, quote=True)

# --- Other Admin Commands (Logs, Ban, Broadcast) ---
@Client.on_message(filters.command("logs") & filters.user(Config.ADMINS))
async def log_handler(client, message):
    if not os.path.exists("log.txt"): return await message.reply("❌ No log file found.", quote=True)
    status = await message.reply("🔍 **Scanning logs...**", quote=True)
    error_lines = []
    with open("log.txt", "r", encoding="utf-8") as f:
        for line in f:
            if any(x in line for x in ["ERROR", "WARNING", "CRITICAL", "Traceback", "Exception"]):
                error_lines.append(line)
            elif line.startswith("  ") or line.startswith("\t"):
                 error_lines.append(line)

    if not error_lines: return await status.edit("✅ **System Healthy**")
    
    temp_file = "bugs.txt"
    with open(temp_file, "w", encoding="utf-8") as f: f.writelines(error_lines)
    await message.reply_document(document=temp_file, caption=f"🐞 Found `{len(error_lines)}` errors.", quote=True)
    os.remove(temp_file)
    await status.delete()

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMINS))
async def broadcast_handler(client, message):
    if not message.reply_to_message: return await message.reply("Reply to a message to broadcast.", quote=True)
    msg = await message.reply("Broadcast started...", quote=True)
    users = await db.get_all_users()
    success, failed = 0, 0
    async for user in users:
        try:
            await message.reply_to_message.copy(user['user_id'])
            success += 1
        except: failed += 1
    await msg.edit(f"**Broadcast Complete**\n✅ Success: {success}\n❌ Failed: {failed}")
