import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from Script import Script
from helper.database import db

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    if await db.is_banned(user_id): return
    
    await db.add_user(user_id, message.from_user.first_name)
    
    lang = await db.get_lang(user_id)
    strs = Script.STRINGS[lang]

    buttons = [
        [InlineKeyboardButton("📦 My Trackings", callback_data="my_trackings")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en"), 
         InlineKeyboardButton("🇮🇳 Hindi", callback_data="set_lang_hi")],
        [InlineKeyboardButton("🆘 Help", callback_data="help_page"), 
         InlineKeyboardButton("ℹ️ About", callback_data="about_page")]
    ]
    if user_id in Config.ADMINS:
        buttons.append([InlineKeyboardButton("📊 Admin Stats", callback_data="admin_stats")])

    await message.reply_text(
        text=strs['start'].format(first_name=message.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )

@Client.on_callback_query(filters.regex(r"^set_lang_"))
async def set_lang_handler(client, callback):
    lang_code = callback.data.split("_")[2]
    await db.set_lang(callback.from_user.id, lang_code)
    
    strs = Script.STRINGS[lang_code]
    await callback.answer(strs['set_lang'], show_alert=True)
    await start_handler(client, callback.message)

@Client.on_callback_query(filters.regex("home_page"))
async def home_cb(client, callback):
    await start_handler(client, callback.message)

@Client.on_callback_query(filters.regex("help_page"))
async def help_cb(client, callback):
    lang = await db.get_lang(callback.from_user.id)
    strs = Script.STRINGS[lang]
    buttons = [[InlineKeyboardButton(strs['back_btn'], callback_data="home_page")]]
    await callback.message.edit_text(strs['help'], reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("about_page"))
async def about_cb(client, callback):
    lang = await db.get_lang(callback.from_user.id)
    strs = Script.STRINGS[lang]
    buttons = [[InlineKeyboardButton(strs['back_btn'], callback_data="home_page")]]
    await callback.message.edit_text(strs['about'], reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("close_menu"))
async def close_cb(client, callback):
    await callback.message.delete()
