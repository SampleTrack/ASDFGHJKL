from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helpers.scraper import fetch_product_details, generate_id
from database import db

# Regex to find URLs
URL_PATTERN = r"https?://[^\s]+"

@Client.on_message(filters.regex(URL_PATTERN) & filters.private)
async def process_link(client, message: Message):
    url = message.matches[0].group(0)
    status_msg = await message.reply("🔎 **Checking Product Details...**")
    
    product_data, error = await fetch_product_details(url)
    
    if error:
        return await status_msg.edit(f"❌ **Error:** {error}")
    
    # Generate a temporary ID for the button callback
    temp_id = generate_id()
    product_data['_id'] = temp_id # Assign ID
    
    caption = (
        f"**🛍 {product_data['name']}**\n\n"
        f"**💲 Price:** {product_data['currency']} {product_data['current_price']}\n"
        f"**🏪 Source:** {product_data['source']}\n\n"
        "__Click the button below to start tracking.__"
    )
    
    # Save temporarily to DB (using the add_tracking logic immediately for simplicity in this version)
    # Ideally, we verify user intent, but to keep code clean:
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Start Tracking", callback_data=f"track_{temp_id}")]
    ])
    
    # We save product data now, but link to user only on button click
    db.products.insert_one(product_data)
    
    await status_msg.delete()
    if product_data['image']:
        await message.reply_photo(product_data['image'], caption=caption, reply_markup=buttons)
    else:
        await message.reply(caption, reply_markup=buttons)

@Client.on_callback_query(filters.regex(r"^track_"))
async def start_tracking_callback(client, callback: CallbackQuery):
    product_id = callback.data.split("_")[1]
    db.add_tracking(callback.from_user.id, {"_id": product_id})
    await callback.answer("✅ Added to your tracking list!")
    await callback.message.edit_reply_markup(None) # Remove button

@Client.on_message(filters.command("my_trackings"))
async def my_trackings_cmd(client, message: Message):
    products = db.get_tracked_products(message.from_user.id)
    
    if not products:
        return await message.reply("❌ You are not tracking any products.")
    
    text = "**📋 Your Tracked Products:**\n\n"
    buttons = []
    
    for p in products:
        buttons.append([InlineKeyboardButton(f"{p['name'][:30]}... - {p['current_price']}", callback_data=f"view_{p['_id']}")])
        
    await message.reply("Select a product to manage:", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^view_"))
async def view_product_callback(client, callback: CallbackQuery):
    product_id = callback.data.split("_")[1]
    p = db.products.find_one({"_id": product_id})
    
    if not p:
        return await callback.answer("❌ Product not found", show_alert=True)
        
    text = (
        f"**🛍 {p['name']}**\n"
        f"**💰 Current Price:** {p['current_price']}\n"
        f"**🔗 Link:** [Click Here]({p['url']})"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗑 Delete Tracking", callback_data=f"del_{product_id}")]
    ])
    await callback.message.edit(text, reply_markup=buttons)

@Client.on_callback_query(filters.regex(r"^del_"))
async def delete_tracking_callback(client, callback: CallbackQuery):
    product_id = callback.data.split("_")[1]
    db.remove_tracking(callback.from_user.id, product_id)
    await callback.message.edit("🗑 **Product removed from tracking.**")
