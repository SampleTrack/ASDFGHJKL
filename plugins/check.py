from pyrogram import Client, filters
from pyrogram.types import Message
from helper.price_checker import run_price_check
from config import Telegram

@Client.on_message(filters.command("check") & filters.user(Telegram.ADMIN))
async def check_product_prices(client: Client, message: Message):
    """Trigger a manual price check (admin only)."""
    try:
        status_msg = await message.reply_text("🔎 **Initializing Price Check...**")
        await run_price_check(client, manual_trigger=True, status_msg=status_msg)
    except Exception as e:
        print(f"Error in check_product_prices: {e}")
        await message.reply_text("An error occurred. Please try again later.")
