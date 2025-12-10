import logging
from pyrogram import Client as app, Client, filters
from pyrogram.types import LinkPreviewOptions
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery,
    LinkPreviewOptions
)
from helper.database import products, users

logger = logging.getLogger(__name__)


async def list_trackings_handler(client: Client, entity):
    """
    Displays the user's list of tracked products.
    This is a helper function called by the command and callback handlers.
    """
    if isinstance(entity, Message):
        user_id = entity.from_user.id
        message = entity
    elif isinstance(entity, CallbackQuery):
        user_id = entity.from_user.id
        message = entity.message
    else:
        return

    try:
        user_doc = users.find_one({"user_id": str(user_id)})
    except Exception as e:
        logger.error(f"DB Error fetching user trackings for user {user_id}: {e}", exc_info=True)
        text = "❌ **Error:** Could not load your tracking list due to a database issue."
        await message.edit_text(text) if isinstance(entity, CallbackQuery) else await message.reply_text(text, quote=True)
        return

    if not user_doc or not user_doc.get("trackings"):
        text = ("😔 **You are not tracking any products yet.**\n"
                "Just send me an Amazon or Flipkart link to start tracking!")
        if isinstance(entity, CallbackQuery):
            await message.edit_text(text)
        else:
            await message.reply_text(text, quote=True)
        return

    tracking_ids = user_doc["trackings"]
    
    try:
        # Fetch product details for all tracked IDs
        product_docs = list(products.find({"_id": {"$in": tracking_ids}}))
    except Exception as e:
        logger.error(f"DB Error fetching product details for user {user_id}: {e}", exc_info=True)
        text = "❌ **Error:** Could not load product details due to a database issue."
        await message.edit_text(text) if isinstance(entity, CallbackQuery) else await message.reply_text(text, quote=True)
        return

    if not product_docs:
        # This handles the case where user has IDs but product collection is empty/references are broken
        text = ("😔 **You are not tracking any products yet.**\n"
                "Looks like your previous trackings were removed. "
                "Send a new link to start!")
        if isinstance(entity, CallbackQuery):
            await message.edit_text(text)
        else:
            await message.reply_text(text, quote=True)
        return

    keyboard_buttons = []
    for doc in product_docs:
        product_name = doc.get('product_name', 'Unnamed Product')
        product_id = doc.get('_id')
        # Truncate long product names to fit on buttons
        keyboard_buttons.append(
            [InlineKeyboardButton(product_name[:60], callback_data=f"info_{product_id}")]
        )

    text = "📝 **Your Tracked Products:**\n\nClick on a product below to see its details."
    keyboard = InlineKeyboardMarkup(keyboard_buttons)

    try:
        if isinstance(entity, CallbackQuery):
            await message.edit_text(text, reply_markup=keyboard)
        else:
            await message.reply_text(text, reply_markup=keyboard, quote=True)
    except Exception as e:
        logger.error(f"Telegram API error sending tracking list to user {user_id}: {e}", exc_info=True)


@app.on_message(filters.command("my_trackings") & filters.private)
async def trackings_command_handler(client: Client, message: Message):
    """Handles the /trackings command."""
    await list_trackings_handler(client, message)


@app.on_callback_query(filters.regex(r"^info_"))
async def product_info_handler(client: Client, callback_query: CallbackQuery):
    """Handles button clicks to show detailed info about a tracked product."""
    product_id = callback_query.data.split("_", 1)[1]
    user_id = callback_query.from_user.id
    
    try:
        product_doc = products.find_one({"_id": product_id, "userid": user_id})
    except Exception as e:
        logger.error(f"DB Error fetching product info {product_id} for user {user_id}: {e}", exc_info=True)
        await callback_query.answer("⚠️ An error occurred while fetching product details.", show_alert=True)
        return


    if not product_doc:
        await callback_query.answer("⚠️ This product is no longer tracked or does not exist.", show_alert=True)
        await callback_query.message.delete()
        return

    api_data = product_doc
    
    # Get the first image URL for the preview link
    images = api_data.get("images", {}).get("initial", [])
    image_preview_link = ""
    if images:
        # Use a zero-width space for an invisible link text
        image_preview_link = f"[\u200b]({images[0]})"
        
    preview_options = LinkPreviewOptions(
        show_above_text=True,
        prefer_small_media =True)

    
    # Construct the message caption with the hidden image link at the top
    caption = (
        f"{image_preview_link}"
        f"**{api_data.get('product_name', 'N/A')}**\n\n"
        f"**Price:** ~~{api_data.get('original_price', {}).get('string', 'N/A')}~~ "
        f"→ **{api_data.get('current_price', {}).get('string', 'N/A')}** "
        f"`({api_data.get('discount_percentage', 'N/A')})`\n"
        f"**Rating:** {api_data.get('rating', 'N/A')} ({api_data.get('reviews_count', 0)} ratings)\n\n"
    )
    
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("❌ Stop Tracking", callback_data=f"stp_tracking_{product_id}"),
            InlineKeyboardButton("🔙 Back", callback_data="back_to_trackings")
        ]]
    )
    

    try:
        await callback_query.message.edit_text(
            text=caption,
            reply_markup=keyboard,
            link_preview_options=preview_options
        )
    except Exception as e:
        logger.error(f"Telegram API error editing product info message for user {user_id}: {e}", exc_info=True)
        await callback_query.answer("⚠️ Could not display product details.", show_alert=True)


@app.on_callback_query(filters.regex(r"^stp_tracking_"))
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


@app.on_callback_query(filters.regex(r"^back_to_trackings"))
async def back_to_trackings_handler(client: Client, callback_query: CallbackQuery):
    """Handles the 'Back' button click."""
    await list_trackings_handler(client, callback_query)
