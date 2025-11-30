from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Local imports
from config import ADMINS, UPDATES_CHANNEL, SUPPORT_CHANNEL
from helper.database import all_users
from Script import script


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
                total = await all_users() 
                await query.answer(
                    f"📊 Bot Statistics\n\nTotal Users: {total}", 
                    show_alert=True
                )
            else:
                await query.answer("❌ You are not an admin.", show_alert=True)
                
    except Exception as e:
        print(f"Callback Error: {e}")
        await query.answer("Message expired or error occurred.", show_alert=True)
        
