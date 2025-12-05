import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from Script import Script
from helper.database import db

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    
    # Check Ban
    if await db.is_banned(user_id):
        return await message.reply(Script.BAN_TXT)

    # Add User & Log
    is_new = await db.add_user(user_id, message.from_user.first_name)
    if is_new and Config.LOG_CHANNEL:
        log_text = Script.NEW_USER_LOG.format(
            name=message.from_user.first_name,
            id=user_id,
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        await client.send_message(Config.LOG_CHANNEL, log_text)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add to Group", url=f"http://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("📦 My Trackings", callback_data="my_trackings"), InlineKeyboardButton("🆘 Help", callback_data="help_data")]
    ])
    
    await message.reply_text(
        text=Script.START_TXT.format(first_name=message.from_user.first_name),
        reply_markup=buttons,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("help") & filters.private)
async def help_handler(client, message):
    if await db.is_banned(message.from_user.id):
        return
        
    await message.reply_text(
        text=Script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_data")]]),
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex("help_data"))
async def help_cb(client, callback):
    await callback.message.edit_text(
        text=Script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_data")]])
    )

@Client.on_callback_query(filters.regex("start_data"))
async def start_cb(client, callback):
    await callback.message.edit_text(
        text=Script.START_TXT.format(first_name=callback.from_user.first_name),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 My Trackings", callback_data="my_trackings"), InlineKeyboardButton("🆘 Help", callback_data="help_data")]
        ])
    )
