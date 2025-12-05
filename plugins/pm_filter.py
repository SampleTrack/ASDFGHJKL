# plugins/callbacks.py
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions

from helper.database import products, users
from plugins.my_trackings import list_trackings_handler
from config import ADMINS, SUPPORT_CHANNEL, UPDATES_CHANNEL
from Script import script
from database.database import db

logger = logging.getLogger(__name__)


# -----------------------
# HELP callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^cb_help$"))
async def cb_help_handler(client: Client, query: CallbackQuery):
    try:
        back_button = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cb_back")]])

        await query.message.edit_text(
            text=script.HELP_TEXT,
            reply_markup=back_button,
            disable_web_page_preview=True
        )
        await query.answer()
    except Exception as e:
        logger.exception(f"cb_help error for user {query.from_user.id}: {e}")


# -----------------------
# ABOUT callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^cb_about$"))
async def cb_about_handler(client: Client, query: CallbackQuery):
    try:
        back_button = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cb_back")]])

        await query.message.edit_text(
            text=script.ABOUT_TEXT,
            reply_markup=back_button,
            disable_web_page_preview=True
        )
        await query.answer()
    except Exception as e:
        logger.exception(f"cb_about error for user {query.from_user.id}: {e}")


# -----------------------
# BACK callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^cb_back$"))
async def cb_back_handler(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    try:
        buttons = [
            [InlineKeyboardButton("🆘 Support", url=SUPPORT_CHANNEL),
             InlineKeyboardButton("🛍 Deals", url=UPDATES_CHANNEL)],
            [InlineKeyboardButton("ℹ️ About", callback_data="cb_about"),
             InlineKeyboardButton("📚 Help", callback_data="cb_help")]
        ]
        if user_id in ADMINS:
            buttons.append([InlineKeyboardButton("📊 Admin Stats", callback_data="cb_stats")])

        await query.message.edit_text(
            text=script.START_TEXT.format(mention=query.from_user.mention),
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        await query.answer()
    except Exception as e:
        logger.exception(f"cb_back error for user {user_id}: {e}")


# -----------------------
# ADMIN STATS callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^cb_stats$"))
async def cb_stats_handler(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    try:
        if user_id not in ADMINS:
            await query.answer("Not an admin", show_alert=True)
            return

        total = await db.get_all_users()
        await query.answer(f"Total users: {total}", show_alert=True)
    except Exception as e:
        logger.exception(f"cb_stats error for user {user_id}: {e}")


# -----------------------
# PRODUCT INFO callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^info_"))
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
        logger.exception(f"info_ error for user {user_id}: {e}")

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
        logger.exception(f"stp_tracking error for user {user_id}: {e}")
    
    await callback_query.answer("✅ Product tracking stopped successfully!", show_alert=False)
    # Refresh the tracking list
    await list_trackings_handler(client, callback_query)


@Client.on_callback_query(filters.regex(r"^back_to_trackings"))
async def back_to_trackings_handler(client: Client, callback_query: CallbackQuery):
    """Handles the 'Back' button click."""
    await list_trackings_handler(client, callback_query)
    
