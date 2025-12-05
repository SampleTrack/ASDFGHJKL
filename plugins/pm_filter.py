# plugins/callbacks.py
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions

from plugins.my_trackings import list_trackings_handler  # import helper to refresh lists
from config import ADMINS, SUPPORT_CHANNEL, UPDATES_CHANNEL  # ensure these constants exist in your config
from Script import script  # script.START_TEXT, HELP_TEXT, ABOUT_TEXT
from database.database import db  # if your project uses db helper for admin stats (used in pm_filter)

logger = logging.getLogger(__name__)


# -----------------------
# HELP callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^cb_help$"))
async def cb_help_handler(client: Client, query: CallbackQuery):
    try:
        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="cb_back")]
        ])

        await query.message.edit_text(
            text=script.HELP_TEXT,
            reply_markup=back_button,
            disable_web_page_preview=True
        )
        await query.answer()
    except Exception as e:
        logger.exception(f"Callback Error (cb_help) for user {query.from_user.id}: {e}")
        try:
            await query.answer("Message expired or error occurred.", show_alert=True)
        except Exception:
            pass


# -----------------------
# ABOUT callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^cb_about$"))
async def cb_about_handler(client: Client, query: CallbackQuery):
    try:
        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="cb_back")]
        ])

        await query.message.edit_text(
            text=script.ABOUT_TEXT,
            reply_markup=back_button,
            disable_web_page_preview=True
        )
        await query.answer()
    except Exception as e:
        logger.exception(f"Callback Error (cb_about) for user {query.from_user.id}: {e}")
        try:
            await query.answer("Message expired or error occurred.", show_alert=True)
        except Exception:
            pass


# -----------------------
# BACK -> START callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^cb_back$"))
async def cb_back_handler(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    try:
        buttons = [
            [
                InlineKeyboardButton("🆘 Support", url=SUPPORT_CHANNEL),
                InlineKeyboardButton("🛍 Deals", url=UPDATES_CHANNEL)
            ],
            [
                InlineKeyboardButton("ℹ️ About", callback_data="cb_about"),
                InlineKeyboardButton("📚 Help", callback_data="cb_help")
            ]
        ]

        if user_id in ADMINS:
            buttons.append(
                [InlineKeyboardButton("📊 Admin Stats", callback_data="cb_stats")]
            )

        await query.message.edit_text(
            text=script.START_TEXT.format(mention=query.from_user.mention),
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        await query.answer()
    except Exception as e:
        logger.exception(f"Callback Error (cb_back) for user {user_id}: {e}")
        try:
            await query.answer("Message expired or error occurred.", show_alert=True)
        except Exception:
            pass


# -----------------------
# ADMIN STATS callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^cb_stats$"))
async def cb_stats_handler(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    try:
        if user_id not in ADMINS:
            await query.answer("❌ You are not an admin.", show_alert=True)
            return

        # db.get_all_users() should be async if using motor/mongo; adjust accordingly
        total = await db.get_all_users()  # make sure this returns an int

        await query.answer(f"📊 Bot Statistics\n\nTotal Users: {total}", show_alert=True)
    except Exception as e:
        logger.exception(f"Callback Error (cb_stats) for user {user_id}: {e}")
        try:
            await query.answer("Message expired or error occurred.", show_alert=True)
        except Exception:
            pass


# -----------------------
# PRODUCT INFO callback
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
        logger.error(
            f"DB Error fetching product info {product_id} for user {user_id}: {e}",
            exc_info=True
        )
        await callback_query.answer(
            "⚠️ An error occurred while fetching product details.",
            show_alert=True
        )
        return

    if not product_doc:
        await callback_query.answer(
            "⚠️ This product is no longer tracked or does not exist.",
            show_alert=True
        )
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
        await callback_query.answer()
    except Exception as e:
        logger.error(
            f"Telegram API error editing product info message for user {user_id}: {e}",
            exc_info=True
        )
        await callback_query.answer("⚠️ Could not display product details.", show_alert=True)


# -----------------------
# STOP TRACKING callback
# -----------------------
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
        logger.error(
            f"DB Error stopping tracking {product_id} for user {user_id}: {e}",
            exc_info=True
        )
        await callback_query.answer(
            "❌ Failed to stop tracking due to a database error.",
            show_alert=True
        )
        return

    await callback_query.answer("✅ Product tracking stopped successfully!", show_alert=False)

    # Refresh the tracking list by calling the listing helper (it expects Message or CallbackQuery)
    try:
        await list_trackings_handler(client, callback_query)
    except Exception as e:
        logger.error(f"Error refreshing tracking list after stop for user {user_id}: {e}", exc_info=True)


# -----------------------
# BACK TO TRACKINGS callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^back_to_trackings$"))
async def back_to_trackings_handler(client: Client, callback_query: CallbackQuery):
    """Handles the 'Back' button click - returns to the trackings list."""
    try:
        await list_trackings_handler(client, callback_query)
        await callback_query.answer()
    except Exception as e:
        logger.error(
            f"Error in back_to_trackings_handler for user {callback_query.from_user.id}: {e}",
            exc_info=True
        )
        await callback_query.answer("⚠️ Could not open trackings.", show_alert=True)

