import random
import string
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, LinkPreviewOptions, Message
from config import Config
from helper.database import db
from helper.utils import fetch_product_info

PENDING_TRACKS = {}
url_pattern = r"https?://[^\s]+"
NO_IMAGE_URL = "https://t4.ftcdn.net/jpg/04/70/29/97/360_F_470299797_UD0eoVMMSUbHCcNJCdv2t8B2g1GVqYgs.jpg"

# -----------------------------------------------------------------------------
# 1. PROCESS LINK & SHOW PREVIEW (Same as before)
# -----------------------------------------------------------------------------
@Client.on_message(filters.regex(url_pattern) & filters.private)
async def process_link(client, message):
    user_id = message.from_user.id
    if await db.is_banned(user_id): return

    url = message.matches[0].group(0)
    status = await message.reply("🔎 **Fetching product details...**", quote=True)

    data = await fetch_product_info(url)
    if not data or not data.get('dealsData'):
        return await status.edit("❌ **Error:** Could not fetch details.")

    product_data = data['dealsData']['product_data']
    currency = data.get('currencySymbol', '₹')
    
    cur_price_str = str(product_data.get('cur_price', '0'))
    try: cur_price_int = int(float(cur_price_str.replace(',', '').replace(currency, '').strip()))
    except: cur_price_int = 0
        
    org_price_str = str(product_data.get('orgi_price', cur_price_str))
    try: org_price_int = int(float(org_price_str.replace(',', '').replace(currency, '').strip()))
    except: org_price_int = 0

    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    real_product_id = str(product_data.get('pid', '')) or ''.join(random.choices(string.ascii_letters, k=12))

    # --- FIX STARTS HERE ---
    # 1. Safely get the list of images (default to empty list if key missing)
    thumbnails = product_data.get('thumbnailImages', [])
    
    # 2. Check if list has items. If yes, take the first one. If no, use the Placeholder.
    image_url = thumbnails[0] if thumbnails else NO_IMAGE_URL
    # --- FIX ENDS HERE ---

    temp_data = {
        "_id": real_product_id,
        "product_name": product_data.get('name', 'Unknown'),
        "url": url,
        "current_price": {"string": cur_price_str, "int": cur_price_int},
        "original_price": {"string": org_price_str, "int": org_price_int},
        "currency": currency,
        "image": image_url, # Now this is guaranteed to have a string, never crash
        "source": product_data.get('site_name', 'Unknown')
    }
    PENDING_TRACKS[session_id] = temp_data

    text = f"**🛒 Preview**\n**Name:** {temp_data['product_name'][:50]}...\n**Price:** {currency}{cur_price_str}\n\n__Start tracking?__"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Start Tracking", callback_data=f"track_{session_id}"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel_track")]
    ])
    
    # Try sending the photo. If the URL (even the placeholder) fails, fall back to text.
    try: 
        await message.reply_photo(photo=temp_data['image'], caption=text, reply_markup=buttons)
        await status.delete() # Only delete loading status if photo sent successfully
    except Exception as e:
        print(f"Image send failed: {e}") # Log the error for debugging
        await status.edit(text, reply_markup=buttons) # Fallback to text editing

# -----------------------------------------------------------------------------
# 2. START TRACKING (Updated to save Price)
# -----------------------------------------------------------------------------
@Client.on_callback_query(filters.regex(r"^track_"))
async def start_tracking_handler(client, callback: CallbackQuery):
    session_id = callback.data.split("_")[1]
    user_id = callback.from_user.id
    product_data = PENDING_TRACKS.get(session_id)

    if not product_data:
        return await callback.answer("⚠️ Session expired.", show_alert=True)

    try:
        try: await db.add_product(product_data)
        except: pass

        # UPDATED: Pass the current integer price here
        current_price = product_data['current_price']['int']
        await db.add_tracking_to_user(user_id, product_data['_id'], current_price)
        
        del PENDING_TRACKS[session_id]

        new_text = f"**✅ Tracking Started!**\n\n**Price:** {product_data['currency']}{product_data['current_price']['string']}"
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("👀 View Details", callback_data=f"view_{product_data['_id']}")]])
        await callback.message.edit_caption(caption=new_text, reply_markup=btn)

    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)

@Client.on_callback_query(filters.regex("cancel_track"))
async def cancel_handler(client, callback):
    await callback.message.delete()

# -----------------------------------------------------------------------------
# 3. LIST TRACKINGS (Updated for New Schema)
# -----------------------------------------------------------------------------
async def get_tracking_list_content(user_id, is_callback=False):
    user = await db.get_user(user_id)
    if not user or not user.get("trackings"):
        return "🤷‍♂️ **Empty List**", [[InlineKeyboardButton("🔙 Back", callback_data="home_page")]] if is_callback else None
    
    track_list = user['trackings'] # This is now a list of objects: [{'id': '...', 'price': 100}]
    buttons = []
    
    for item in track_list:
        # Check if item is dict (New Schema) or str (Old Schema - Backward compatibility)
        tid = item['id'] if isinstance(item, dict) else item
        
        prod = await db.get_product(tid)
        if prod:
            buttons.append([InlineKeyboardButton(f"📦 {prod['product_name'][:30]}...", callback_data=f"view_{tid}")])
    
    if is_callback:
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="home_page"), InlineKeyboardButton("❌ Close", callback_data="close_menu")])
    return "**📋 Your Tracked Products:**", buttons

@Client.on_message(filters.command("trackings") & filters.private)
async def trackings_command(client, message: Message):
    text, buttons = await get_tracking_list_content(message.from_user.id)
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None)

@Client.on_callback_query(filters.regex("my_trackings"))
async def my_trackings_cb(client, callback):
    text, buttons = await get_tracking_list_content(callback.from_user.id, is_callback=True)
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# -----------------------------------------------------------------------------
# 4. VIEW PRODUCT DETAILS (Updated to show Added Price)
# -----------------------------------------------------------------------------
@Client.on_callback_query(filters.regex(r"^view_"))
async def view_product(client, callback):
    prod_id = callback.data.split("_")[1]
    prod = await db.get_product(prod_id)
    user = await db.get_user(callback.from_user.id)
    
    if not prod:
        await callback.answer("❌ Product not found.", show_alert=True)
        return await my_trackings_cb(client, callback)

    # 1. Get Details from Product DB
    currency = prod.get('currency', '₹')
    curr_price = prod['current_price']['int']
    curr_price_str = prod['current_price']['string']
    
    # 2. Get "Added Price" from User DB
    added_price = 0
    for item in user.get('trackings', []):
        # Handle both object and string format (migration safety)
        if isinstance(item, dict) and item['id'] == prod_id:
            added_price = item.get('added_price', 0)
            break
        elif isinstance(item, str) and item == prod_id:
            added_price = 0 # Old data
            break
            
    # 3. Calculate Change from "Added Price"
    if added_price > 0:
        if curr_price < added_price:
            diff = added_price - curr_price
            percent = int((diff / added_price) * 100)
            added_txt = f"📉 **Dropped:** {currency}{diff} ({percent}%) since you added."
        elif curr_price > added_price:
            diff = curr_price - added_price
            percent = int((diff / added_price) * 100)
            added_txt = f"📈 **Increased:** {currency}{diff} ({percent}%) since you added."
        else:
            added_txt = "➖ **No Change** since you added."
        
        added_price_display = f"{currency}{added_price}"
    else:
        added_txt = "⚠️ Price history not available."
        added_price_display = "N/A"

    img_link = f"[\u200b]({prod['image']})" if prod.get('image') else ""

    text = (
        f"{img_link}"
        f"**📦 {prod['product_name']}**\n\n"
        f"🏪 **Source:** {prod['source']}\n"
        f"📌 **Added At:** {added_price_display}\n"
        f"💰 **Current:** {currency}{curr_price_str}\n\n"
        f"{added_txt}"
    )

    buttons = [
        [InlineKeyboardButton("🔗 Buy Now / Check Link", url=prod['url'])],
        [InlineKeyboardButton("🗑️ Remove Tracking", callback_data=f"del_{prod_id}")],
        [InlineKeyboardButton("🔙 Back to List", callback_data="my_trackings")]
    ]

    preview = LinkPreviewOptions(url=prod.get('image'), show_above_text=True, prefer_large_media=True) if prod.get('image') else None
    
    try: await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), link_preview_options=preview)
    except: await callback.message.edit_text(text.replace("\u200b", ""), reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^del_"))
async def delete_product(client, callback):
    prod_id = callback.data.split("_")[1]
    await db.delete_product_tracking(callback.from_user.id, prod_id)
    await callback.answer("✅ Removed!", show_alert=False)
    await my_trackings_cb(client, callback)

