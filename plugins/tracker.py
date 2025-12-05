import random
import string
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import Config
from helper.database import db
from helper.utils import fetch_product_info

# Temporary dictionary to store data before the user clicks "Start Tracking"
# Structure: {'unique_session_id': {product_data}}
PENDING_TRACKS = {}

# Regex for URLs
url_pattern = r"https?://[^\s]+"

@Client.on_message(filters.regex(url_pattern) & filters.private)
async def process_link(client, message):
    user_id = message.from_user.id
    if await db.is_banned(user_id):
        return

    url = message.matches[0].group(0)
    status = await message.reply("🔎 **Fetching product details...**", quote=True)

    # 1. Fetch Data from API
    data = await fetch_product_info(url)
    
    if not data or not data.get('dealsData'):
        return await status.edit("❌ **Error:** Could not fetch product details. The link might be invalid or unsupported.")

    product_data = data['dealsData']['product_data']
    currency = data.get('currencySymbol', '₹')
    
    # 2. Parse Price
    price_str = str(product_data.get('cur_price', '0'))
    try:
        price_int = int(float(price_str.replace(',', '').replace(currency, '').strip()))
    except:
        price_int = 0

    # 3. Create a Unique Session ID for this specific interaction
    # This acts as a key to retrieve the data later when button is clicked
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    # 4. Prepare Data Object (But don't save to DB yet!)
    # We use the product's PID (or URL hash) as the real DB ID to prevent duplicates
    real_product_id = str(product_data.get('pid', '')) or ''.join(random.choices(string.ascii_letters, k=12))

    temp_data = {
        "_id": real_product_id, # The ID that will be used in MongoDB
        "product_name": product_data.get('name', 'Unknown'),
        "url": url,
        "current_price": {"string": price_str, "int": price_int},
        "currency": currency,
        "image": product_data.get('thumbnailImages', [''])[0],
        "source": product_data.get('site_name', 'Unknown')
    }

    # Store in memory
    PENDING_TRACKS[session_id] = temp_data

    # 5. Create Buttons
    text = f"""
**🛒 Product Preview**

**Name:** {temp_data['product_name'][:60]}...
**Price:** {currency}{price_str}
**Source:** {temp_data['source']}

__Do you want to start tracking this item?__
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Start Tracking", callback_data=f"track_{session_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_track")]
    ])
    
    # 6. Send Preview
    try:
        await message.reply_photo(
            photo=temp_data['image'], 
            caption=text, 
            reply_markup=buttons
        )
        await status.delete()
    except Exception as e:
        # Fallback if image fails
        await status.edit(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex(r"^track_"))
async def start_tracking_handler(client, callback: CallbackQuery):
    """
    Triggered when user clicks 'Start Tracking'
    """
    session_id = callback.data.split("_")[1]
    user_id = callback.from_user.id

    # 1. Retrieve data from memory
    product_data = PENDING_TRACKS.get(session_id)

    if not product_data:
        return await callback.answer("⚠️ Session expired. Please send the link again.", show_alert=True)

    try:
        # 2. Add to Database
        # Note: add_product might fail if it exists, so we wrap in try/catch or handle inside db function
        # Using try/except is safer here in case your DB logic throws error on duplicate key
        try:
            await db.add_product(product_data)
        except:
            pass # Product likely exists already, which is fine

        # 3. Link to User
        await db.add_tracking_to_user(user_id, product_data['_id'])

        # 4. Clean up memory
        del PENDING_TRACKS[session_id]

        # 5. Edit Message to confirm
        new_text = f"""
**✅ Tracking Started!**

**Name:** {product_data['product_name'][:50]}...
**Current Price:** {product_data['currency']}{product_data['current_price']['string']}

I will notify you when the price drops.
"""
        await callback.message.edit_caption(
            caption=new_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ Remove Tracking", callback_data=f"del_{product_data['_id']}")]]),
        )

    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)


@Client.on_callback_query(filters.regex("cancel_track"))
async def cancel_handler(client, callback):
    await callback.message.delete()


# --- EXISTING DELETE AND LIST HANDLERS ---

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
