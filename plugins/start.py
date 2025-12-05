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

    buttons = [
        [
            InlineKeyboardButton("💬 Support Chat", url="https://t.me/YourSupportChat"),
            InlineKeyboardButton("📢 Updates", url="https://t.me/YourUpdatesChannel")
        ],
        [
            InlineKeyboardButton("🆘 Help", callback_data="help_page"),
            InlineKeyboardButton("ℹ️ About", callback_data="about_page")
        ],
        [
            InlineKeyboardButton("📦 My Trackings", callback_data="my_trackings")
        ]
    ]

    # Add Admin Stats button ONLY if user is Admin
    if user_id in Config.ADMINS:
        buttons.append([InlineKeyboardButton("📊 Admin Stats", callback_data="admin_stats")])

    await message.reply_text(
        text=Script.START_TXT.format(first_name=message.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex("home_page"))
async def home_cb(client, callback):
    # Re-generate the start menu (copy logic from start_handler)
    user_id = callback.from_user.id
    buttons = [
        [InlineKeyboardButton("💬 Support Chat", url="https://t.me/YourSupport"), InlineKeyboardButton("📢 Updates", url="https://t.me/YourChannel")],
        [InlineKeyboardButton("🆘 Help", callback_data="help_page"), InlineKeyboardButton("ℹ️ About", callback_data="about_page")],
        [InlineKeyboardButton("📦 My Trackings", callback_data="my_trackings")]
    ]
    if user_id in Config.ADMINS:
        buttons.append([InlineKeyboardButton("📊 Admin Stats", callback_data="admin_stats")])
    
    await callback.message.edit_text(
        text=Script.START_TXT.format(first_name=callback.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("help_page"))
async def help_cb(client, callback):
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="home_page"), InlineKeyboardButton("❌ Cancel", callback_data="close_menu")]]
    await callback.message.edit_text(Script.HELP_TXT, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("about_page"))
async def about_cb(client, callback):
    buttons = [[InlineKeyboardButton("🔙 Back", callback_data="home_page"), InlineKeyboardButton("❌ Cancel", callback_data="close_menu")]]
    await callback.message.edit_text(Script.ABOUT_TXT, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("close_menu"))
async def close_cb(client, callback):
    await callback.message.delete()
