import os
import time
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# Local imports
from config import ADMINS, LOG_CHANNEL, UPDATES_CHANNEL, SUPPORT_CHANNEL
from helper.database import add_user, all_users
from script import Script


def start_buttons(user_id):
    """Generates buttons for start message. Adds Admin button if user is Admin."""
    buttons = [
        [
            InlineKeyboardButton("🆘 Support", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("🛍 Deals", url=UPDATES_CHANNEL)
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="cb_about"),
            InlineKeyboardButton("📚 Help", callback_data="cb_help")
        ]
    ]
    
    # Admin Only Button logic
    if user_id in ADMINS:
        buttons.append([InlineKeyboardButton("📊 Admin Stats", callback_data="cb_stats")])
        
    return InlineKeyboardMarkup(buttons)

back_button = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔙 Back", callback_data="cb_back")]
])

# --- COMMAND HANDLERS ---

@Client.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    """Reply start message with buttons"""
    try:
        user_id = message.from_user.id
        await add_user(user_id, client)
        
        await message.reply_text(
            text=Script.START_TEXT.format(mention=message.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=start_buttons(user_id),
            quote=True
        )
    except Exception as e:
        print(f"Error in start: {e}")
        await message.reply("An error occurred.", quote=True)


@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """Reply help message"""
    try:
        await message.reply_text(
            text=Script.HELP_TEXT,
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=back_button,
            quote=True
        )
    except Exception as e:
        print(f"Error in help: {e}")
        await message.reply("An error occurred.", quote=True)


@Client.on_message(filters.command("about") & filters.private)
async def about_command(client: Client, message: Message):
    """Reply about message"""
    try:
        await message.reply_text(
            text=Script.ABOUT_TEXT,
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=back_button,
            quote=True
        )
    except Exception as e:
        print(f"Error in about: {e}")
        await message.reply("An error occurred.", quote=True)


# --- ADMIN ONLY COMMANDS ---

@Client.on_message(filters.command("logs") & filters.user(ADMINS))
async def logs(client: Client, message: Message):
    """Send the error log file"""
    try:
        log_file = "bot.log" 
        if os.path.exists(log_file):
            await message.reply_document(
                document=log_file,
                caption="📄 **Here is your bot log file.**",
                quote=True
            )
        else:
            await message.reply("❌ No log file found.", quote=True)
    except Exception as e:
        print(f"Error in logs: {e}")
        await message.reply(f"Failed to send logs: {e}", quote=True)


@Client.on_message(filters.command("ping") & filters.user(ADMINS))
async def ping(client: Client, message: Message):
    """Check bot latency"""
    try:
        start_time = time.time()
        msg = await message.reply("🏓 Pinging...", quote=True)
        end_time = time.time()
        
        latency = round((end_time - start_time) * 1000)
        await msg.edit(f"🏓 **Pong!**\nLatency: `{latency}ms`")
    except Exception as e:
        print(f"Error in ping: {e}")
        
