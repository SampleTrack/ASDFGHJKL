import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import db
from config import Config

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):
    user = message.from_user
    db.add_user(user.id, user.first_name)
    
    text = (
        f"**Hello {user.first_name}! 👋**\n\n"
        "I am a **Price Tracker Bot**. I can track prices for Amazon & Flipkart products.\n\n"
        "**How to use:**\n"
        "1. Send me a product link.\n"
        "2. I will start tracking it.\n"
        "3. I will notify you when the price drops!"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Updates", url="https://t.me/YourChannel"), InlineKeyboardButton("🆘 Support", url="https://t.me/YourSupport")],
        [InlineKeyboardButton("🔎 Check Trackings", callback_data="my_trackings")]
    ])
    await message.reply(text, reply_markup=buttons)

@Client.on_message(filters.command("help") & filters.private)
async def help_handler(client, message: Message):
    text = (
        "**🛠 Help Menu**\n\n"
        "/start - Restart the bot\n"
        "/my_trackings - View your tracked items\n"
        "/ping - Check bot latency\n"
        "/suggest [text] - Send a suggestion to admin\n\n"
        "**Just paste a product link to start tracking!**"
    )
    await message.reply(text)

@Client.on_message(filters.command("ping"))
async def ping_handler(client, message: Message):
    start = time.time()
    msg = await message.reply("🏓 Pong!")
    end = time.time()
    await msg.edit(f"🏓 **Pong!**\nLatency: `{round((end - start) * 1000)}ms`")

@Client.on_message(filters.command("suggest") & filters.private)
async def suggest_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("⚠️ **Usage:** `/suggest Make the bot faster`")
    
    suggestion = message.text.split(" ", 1)[1]
    user = message.from_user
    
    log_text = (
        f"**💡 New Suggestion**\n\n"
        f"**From:** {user.mention} (`{user.id}`)\n"
        f"**Message:** {suggestion}"
    )
    
    try:
        await client.send_message(Config.LOG_CHANNEL_ID, log_text)
        await message.reply("✅ **Your suggestion has been sent to the admin!**")
    except Exception:
        await message.reply("❌ **Error:** Log Channel not set correctly.")
