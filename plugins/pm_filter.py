import logging
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, LinkPreviewOptions

# Local imports
from config import ADMINS, UPDATES_CHANNEL, SUPPORT_CHANNEL
from database.database import db  # Assuming this is your admin stats db
from helper.database import products, users # Needed for tracking logic
from Script import script

# Import the shared handler from the other file
from plugins.my_trackings import list_trackings_handler 

logger = logging.getLogger(__name__)

# --- HELPERS ---

def get_start_buttons(user_id):
    """Helper to generate start buttons for the back callback"""
    buttons = [
        [
            InlineKeyboardButton("🆘 Support", url=SUPPORT_CHANNEL), # Fixed variable name based on context
            InlineKeyboardButton("🛍 Deals", url=UPDATES_CHANNEL) # Fixed variable name based on context
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


# --- MASTER CALLBACK HANDLER ---

@Client.on_callback_query()
async def all_callback_handlers(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    
    try:
        # ==================================================================
        #  SECTION 1: PM FILTER & MENUS (Help, About, Start)
        # ==================================================================
        
        if data == "cb_help":
            await query.message.edit_text(
                text=script.HELP_TEXT,
                reply_markup=back_button,
                disable_web_page_preview=True
            )
        
        elif data == "cb_about":
            await query.message.edit_text(
                text=script.ABOUT_TEXT,
                reply_markup=back_button,
                disable_web_page_preview=True
            )
            
        elif data == "cb_back":
            await query.message.edit_text(
                text=script.START_TEXT.format(mention=query.from_user.mention),
                reply_markup=get_start_buttons(user_id),
                disable_web_page_preview=True
            )
            
        elif data == "cb_stats":
            if user_id in ADMINS:
                total = await db.get_all_users() 
                await query.answer(
                    f"📊 Bot Statistics\n\nTotal Users: {total}", 
                    show_alert=True
                )
            else:
                await query.answer("❌ You are not an admin.", show_alert=True)

        # ==================================================================
        #  SECTION 2: TRACKING SYSTEM (Info, Stop, Back to List)
        # ==================================================================

        elif data.startswith("info_"):
            product_id = data.split("_", 1)[1]
            try:
                product_doc = products.find_one({"_id": product_id, "userid": user_id})
            except Exception as e:
                logger.error(f"DB Error fetching product info {product_id}: {e}")
                await query.answer("⚠️ Error fetching details.", show_alert=True)
                return

            if not product_doc:
                await query.answer("⚠️ Product no longer tracked.", show_alert=True)
                await query.message.delete()
                return

            api_data = product_doc
            images = api_data.get("images", {}).get("initial", [])
            image_preview_link = f"[\u200b]({images[0]})" if images else ""
            
            preview_options = LinkPreviewOptions(show_above_text=True, prefer_small_media=True)

            caption = (
                f"{image_preview_link}"
                f"**{api_data.get('product_name', 'N/A')}**\n\n"
                f"**Price:** ~~{api_data.get('original_price', {}).get('string', 'N/A')}~~ "
                f"→ **{api_data.get('current_price', {}).get('string', 'N/A')}** "
                f"`({api_data.get('discount_percentage', 'N/A')})`\n"
                f"**Rating:** {api_data.get('rating', 'N/A')} ({api_data.get('reviews_count', 0)} ratings)\n\n"
            )
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("❌ Stop Tracking", callback_data=f"stp_tracking_{product_id}"),
                    InlineKeyboardButton("🔙 Back", callback_data="back_to_trackings")
                ]
            ])

            await query.message.edit_text(
                text=caption,
                reply_markup=keyboard,
                link_preview_options=preview_options
            )

        elif data.startswith("stp_tracking_"):
            product_id = data.replace("stp_tracking_", "", 1)
            try:
                users.update_one(
                    {"user_id": str(user_id)},
                    {"$pull": {"trackings": product_id}}
                )
            except Exception as e:
                logger.error(f"DB Error stopping tracking {product_id}: {e}")
                await query.answer("❌ DB Error.", show_alert=True)
                return
            
            await query.answer("✅ Product tracking stopped!", show_alert=False)
            # Refresh the list using the imported handler
            await list_trackings_handler(client, query)

        elif data == "back_to_trackings":
            # Call the shared handler from my_trackings.py
            await list_trackings_handler(client, query)

    except Exception as e:
        logger.error(f"Callback Global Error: {e}", exc_info=True)
        await query.answer("An error occurred.", show_alert=True)
        
