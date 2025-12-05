import random
import string
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from config import Config
from helper.database import db
from helper.utils import fetch_product_info

# Regex for URLs
url_pattern = r"https?://[^\s]+"

@Client.on_message(filters.regex(url_pattern) & filters.private)
async def process_link(client, message):
    user_id = message.from_user.id
    if await db.is_banned(user_id):
        return

    url = message.matches[0].group(0)
    status = await message.reply("🔎 **Fetching details...**")

    data = await fetch_product_info(url)
    
    if not data or not data.get('dealsData'):
        return await status.edit("❌ **Error:** Could not fetch product details. Unsupported link or API error.")

    product_data = data['dealsData']['product_data']
    currency = data.get('currencySymbol', '₹')
    
    # Generate unique ID for tracking
    tracking_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    # Clean Price
    price_str = str(product_data.get('cur_price', '0'))
    try:
        price_int = int(float(price_str.replace(',', '').replace(currency, '').strip()))
    except:
        price_int = 0

    # Save to Pending dict (in memory) or directly save to DB with a flag. 
    # For simplicity, we save directly but users must confirm via button if needed, 
    # but here we assume sending link = want to track.
    
    db_item = {
        "_id": tracking_id,
        "product_name": product_data.get('name', 'Unknown'),
        "url": url,
        "current_price": {"string": price_str, "int": price_int},
        "currency": currency,
        "image": product_data.get('thumbnailImages', [''])[0],
        "source": product_data.get('site_name', 'Unknown')
    }
    
    # Save Product
    await db.add_product(db_item)
    # Link to User
    await db.add_tracking_to_user(user_id, tracking_id)

    text = f"""
**✅ Product Added to Tracking!**

**Name:** {db_item['product_name'][:50]}...
**Price:** {currency}{price_str}
**Source:** {db_item['source']}

I will notify you when the price changes.
"""
    
    keyb = InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ Remove", callback_data=f"del_{tracking_id}")]])
    
    # Attempt to send with image
    try:
        await message.reply_photo(photo=db_item['image'], caption=text, reply_markup=keyb)
        await status.delete()
    except:
        await status.edit(text, reply_markup=keyb)

@Client.on_callback_query(filters.regex(r"^del_"))
async def delete_track(client, callback):
    track_id = callback.data.split("_")[1]
    await db.delete_product_tracking(callback.from_user.id, track_id)
    await callback.answer("Deleted!")
    await callback.message.delete()

@Client.on_callback_query(filters.regex("my_trackings"))
async def my_trackings(client, callback):
    user = await db.get_user(callback.from_user.id)
    if not user or not user.get("trackings"):
        return await callback.answer("You are not tracking any items.", show_alert=True)
    
    track_ids = user['trackings']
    if not track_ids:
         return await callback.answer("You are not tracking any items.", show_alert=True)

    text = "**📦 Your Tracked Items:**\n\n"
    
    for tid in track_ids:
        prod = await db.get_product(tid)
        if prod:
            text += f"🔹 [{prod['product_name'][:20]}...]({prod['url']}) - {prod['currency']}{prod['current_price']['string']} (/del_{tid})\n"
            
    await callback.message.edit_text(text, disable_web_page_preview=True)
