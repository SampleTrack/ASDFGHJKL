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
async def product_info_handler(client: Client, cq: CallbackQuery):
    product_id = cq.data.split("_", 1)[1]
    user_id = cq.from_user.id

    try:
        product_doc = products.find_one({"_id": product_id, "userid": user_id})
        if not product_doc:
            await cq.answer("Not available", show_alert=True)
            return

        images = product_doc.get("images", {}).get("initial", [])
        preview = f"[\u200b]({images[0]})" if images else ""

        caption = (
            f"{preview}**{product_doc.get('product_name', 'N/A')}**\n\n"
            f"**Price:** ~~{product_doc['original_price']['string']}~~ → "
            f"**{product_doc['current_price']['string']}** "
            f"({product_doc.get('discount_percentage', 'N/A')})\n"
            f"**Rating:** {product_doc.get('rating')} "
            f"({product_doc.get('reviews_count', 0)} reviews)\n"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Stop Tracking", callback_data=f"stp_tracking_{product_id}"),
             InlineKeyboardButton("🔙 Back", callback_data="back_to_trackings")]
        ])

        await cq.message.edit_text(
            caption,
            reply_markup=keyboard,
            link_preview_options=LinkPreviewOptions(show_above_text=True)
        )
        await cq.answer()
    except Exception as e:
        logger.exception(f"info_ error for user {user_id}: {e}")


# -----------------------
# STOP TRACKING callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^stp_tracking_"))
async def stop_tracking_handler(client: Client, cq: CallbackQuery):
    product_id = cq.data.replace("stp_tracking_", "")
    user_id = cq.from_user.id

    try:
        users.update_one({"user_id": str(user_id)}, {"$pull": {"trackings": product_id}})

        await cq.answer("Stopped!")
        await list_trackings_handler(client, cq)
    except Exception as e:
        logger.exception(f"stp_tracking error for user {user_id}: {e}")


# -----------------------
# BACK TO TRACKINGS callback
# -----------------------
@Client.on_callback_query(filters.regex(r"^back_to_trackings$"))
async def back_to_trackings_handler(client: Client, cq: CallbackQuery):
    try:
        await list_trackings_handler(client, cq)
        await cq.answer()
    except Exception as e:
        logger.exception(f"back_to_trackings error for user {cq.from_user.id}: {e}")







