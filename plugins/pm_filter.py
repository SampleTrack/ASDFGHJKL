from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Local imports
from config import ADMINS, UPDATES_CHANNEL, SUPPORT_CHANNEL
from database.database import db
from Script import script

import logging
from pyrogram import Client, filters
from pyrogram.types import LinkPreviewOptions
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup, InlineKeyboardButton,
    LinkPreviewOptions
)
from helper.database import products, users

logger = logging.getLogger(__name__)

def get_start_buttons(user_id):
    """Helper to generate start buttons for the back callback"""
    buttons = [
        [
            InlineKeyboardButton("🆘 Support", url=SUPPORT_LINK),
            InlineKeyboardButton("🛍 Deals", url=DEALS_LINK)
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="cb_about"),
            InlineKeyboardButton("📚 Help", callback_data="cb_help")
        ]
    ]
    if user_id in ADMINS:
        buttons.append([InlineKeyboardButton("📊 Admin Stats", callback_data="cb_stats")])
    return InlineKeyboardMarkup(buttons)

back_button = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔙 Back", callback_data="cb_back")]
])

@Client.on_callback_query(filters.regex(r"^info_"))
async def product_info_handler(client: Client, callback_query: CallbackQuery):
    """Handles button clicks to show detailed info about a tracked product."""
    
    # Extract ID from callback data (e.g., "info_12345" -> "12345")
    try:
        product_id = callback_query.data.split("_", 1)[1]
    except IndexError:
        await callback_query.answer("⚠️ Invalid request data.", show_alert=True)
        return

    user_id = callback_query.from_user.id

    # 1. Fetch Product from Database
    try:
        product_doc = products.find_one({"_id": product_id, "userid": user_id})
    except Exception as e:
        logger.error(f"DB Error fetching product info {product_id} for user {user_id}: {e}", exc_info=True)
        await callback_query.answer("⚠️ An error occurred while fetching product details.", show_alert=True)
        return

    # 2. Check if product exists
    if not product_doc:
        await callback_query.answer("⚠️ This product is no longer tracked or does not exist.", show_alert=True)
        try:
            await callback_query.message.delete()
        except:
            pass
        return

    api_data = product_doc

    # 3. FIX: Handle Images (List vs Dictionary) safely
    # This block fixes the AttributeError by checking the data type
    raw_images = api_data.get("images", [])
    image_list = []

    if isinstance(raw_images, list):
        # Case 1: Database has ["url1", "url2"]
        image_list = raw_images
    elif isinstance(raw_images, dict):
        # Case 2: Database has {"initial": ["url1"], "hi_res": [...]}
        image_list = raw_images.get("initial", [])

    # 4. Generate invisible preview link
    image_preview_link = ""
    if image_list and len(image_list) > 0:
        # Use a zero-width space [\u200b] for an invisible link text
        image_preview_link = f"[\u200b]({image_list[0]})"

    preview_options = LinkPreviewOptions(
        show_above_text=True,
        prefer_small_media=True
    )

    # 5. Extract Data safely for the caption
    name = api_data.get('product_name', 'N/A')
    original_price = api_data.get('original_price', {}).get('string', 'N/A')
    current_price = api_data.get('current_price', {}).get('string', 'N/A')
    discount = api_data.get('discount_percentage', 'N/A')
    rating = api_data.get('rating', 'N/A')
    reviews = api_data.get('reviews_count', 0)

    # Construct the message caption
    caption = (
        f"{image_preview_link}"
        f"**{name}**\n\n"
        f"**Price:** ~~{original_price}~~ → **{current_price}** `({discount})`\n"
        f"**Rating:** {rating} ({reviews} ratings)\n\n"
    )

    # 6. Create Keyboard
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("❌ Stop Tracking", callback_data=f"stp_tracking_{product_id}"),
            InlineKeyboardButton("🔙 Back", callback_data="back_to_trackings")
        ]]
    )

    # 7. Edit the message
    try:
        await callback_query.message.edit_text(
            text=caption,
            reply_markup=keyboard,
            link_preview_options=preview_options
        )
    except Exception as e:
        logger.error(f"Telegram API error editing product info for user {user_id}: {e}", exc_info=True)
        await callback_query.answer("⚠️ Could not display product details.", show_alert=True)
        

@Client.on_callback_query(filters.regex(r"^stp_tracking_"))
async def stop_tracking_handler(client: Client, callback_query: CallbackQuery):
    """Handles the 'Stop Tracking' button click."""
    product_id = callback_query.data.replace("stp_tracking_", "", 1)
    user_id = callback_query.from_user.id
    
    try:
        users.update_one(
            {"user_id": str(user_id)},
            {"$pull": {"trackings": product_id}}
        )
    except Exception as e:
        logger.error(f"DB Error stopping tracking {product_id} for user {user_id}: {e}", exc_info=True)
        await callback_query.answer("❌ Failed to stop tracking due to a database error.", show_alert=True)
        return
    
    await callback_query.answer("✅ Product tracking stopped successfully!", show_alert=False)
    # Refresh the tracking list
    await list_trackings_handler(client, callback_query)


@Client.on_callback_query(filters.regex(r"^back_to_trackings"))
async def back_to_trackings_handler(client: Client, callback_query: CallbackQuery):
    """Handles the 'Back' button click."""
    await list_trackings_handler(client, callback_query)

# --- CALLBACK HANDLER ---

@Client.on_callback_query()
async def callback_handlers(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    
    try:
        # Help Button
        if data == "cb_help":
            await query.message.edit_text(
                text=script.HELP_TEXT,
                reply_markup=back_button,
                disable_web_page_preview=True
            )
        
        # About Button
        elif data == "cb_about":
            await query.message.edit_text(
                text=script.ABOUT_TEXT,
                reply_markup=back_button,
                disable_web_page_preview=True
            )
            
        # Back Button (Returns to Start)
        elif data == "cb_back":
            await query.message.edit_text(
                text=script.START_TEXT.format(mention=query.from_user.mention),
                reply_markup=get_start_buttons(user_id),
                disable_web_page_preview=True
            )
            
        # Admin Stats Button (Popup)
        elif data == "cb_stats":
            if user_id in ADMINS:
                total = await db.get_all_users() 
                await query.answer(
                    f"📊 Bot Statistics\n\nTotal Users: {total}", 
                    show_alert=True
                )
            else:
                await query.answer("❌ You are not an admin.", show_alert=True)
                
    except Exception as e:
        print(f"Callback Error: {e}")
        await query.answer("Message expired or error occurred.", show_alert=True)
        
