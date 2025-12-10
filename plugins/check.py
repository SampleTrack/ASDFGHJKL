from pyrogram import Client, filters
from pyrogram.types import Message
from helper.price_checker import run_price_check
from config import Telegram

@Client.on_message(filters.command("check") & filters.user(Telegram.ADMIN))
async def check_product_prices(client: Client, message: Message):
    status_msg = await message.reply_text("🔎 **Initializing Price Check...**")
    await run_price_check(client, manual_trigger=True, status_msg=status_msg)
