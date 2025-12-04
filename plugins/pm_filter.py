# plugins/callbacks.py
import logging
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import LinkPreviewOptions
from helper.database import products, users  # adjust import path if your project uses a different module
from plugins.my_trackings import list_trackings_handler  # import helper to refresh lists
from config import ADMINS, SUPPORT_LINK, DEALS_LINK  # ensure these constants exist in your config
from Script import script  # script.START_TEXT, HELP_TEXT, ABOUT_TEXT
from database.database import db  # if your project uses db helper for admin stats (used in pm_filter)

logger = logging.getLogger(__name__)

def get_start_buttons(user_id):
    """Helper to generate start buttons for the start/back menu."""
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


# Generic callback handler for UI buttons (help / about / back / admin stats)
@Client.on_callback_query()
async def callback_handlers(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    try:
        # HELP
        if data == "cb_help":
            await query.message.edit_text(
                text=script.HELP_TEXT,
                reply_markup=back_button,
                disable_web_page_preview=True
            )

        # ABOUT
        elif data == "cb_about":
            await query.message.edit_text(
                text=script.ABOUT_TEXT,
                reply_markup=back_button,
                disable_web_page_preview=True
            )

        # BACK -> start text with start buttons
        elif data == "cb_back":
            await query.message.edit_text(
                text=script.START_TEXT.format(mention=query.from_user.mention),
                reply_markup=get_start_buttons(user_id),
                disable_web_page_preview=True
            )

        # Admin stats (popup)
        elif data == "cb_stats":
            if user_id in ADMINS:
                # db.get_all_users() should be async if using motor/mongo; adjust accordingly
                total = await db.get_all_users()
                await query.answer(f"📊 Bot Statistics\n\nTotal Users: {total}", show_alert=True)
            else:
                await query.answer("❌ You are not an admin.", show_alert=True)

        # Other callbacks pass through (some callbacks for product info are handled in dedicated handlers below)
        else:
            # If it's not one of the above, do nothing here; other handlers may intercept via regex filters
            return

    except Exception as e:
        logger.exception(f"Callback Error for user {user_id}: {e}")
        # best-effort reply
        try:
            await query.answer("Message expired or error occurred.", show_alert=True)
        except Exception:
            logger.debug("Failed to answer callback on error.")


# -----------------------
# Product-related callbacks (moved from my_trackings to central callbacks file)
# -----------------------

@Client.on_callback_query(filters.regex(r"^info_"))
async def product_info_handler(client: Client, callback_query: CallbackQuery):
    """Handles button clicks to show detailed info about a tracked product."""
    product_id = callback_query.data.split("_", 1)[1]
    user_id = callback_query.from_user.id

    try:
        # product documents might store userid as int or str; match what you use in DB
        product_doc = products.find_one({"_id": product_id, "userid": user_id})
    except Exception as e:
        logger.error(f"DB Error fetching product info {product_id} for user {user_id}: {e}", exc_info=True)
        await callback_query.answer("⚠️ An error occurred while fetching product details.", show_alert=True)
        return

    if not product_doc:
        await callback_query.answer("⚠️ This product is no longer tracked or does not exist.", show_alert=True)
        # try to remove the message to clean up
        try:
            await callback_query.message.delete()
        except Exception:
            pass
        return

    api_data = product_doc

    # Get the first image URL for the preview link (if any)
    images = api_data.get("images", {}).get("initial", [])
    image_preview_link = ""
    if images:
        image_preview_link = f"[\u200b]({images[0]})"  # zero-width link to trigger preview

    preview_options = LinkPreviewOptions(show_above_text=True, prefer_small_media=True)

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
    # Refresh the tracking list by calling the listing helper (it expects Message or CallbackQuery)
    await list_trackings_handler(client, callback_query)


@Client.on_callback_query(filters.regex(r"^back_to_trackings"))
async def back_to_trackings_handler(client: Client, callback_query: CallbackQuery):
    """Handles the 'Back' button click - returns to the trackings list."""
    await list_trackings_handler(client, callback_query)
