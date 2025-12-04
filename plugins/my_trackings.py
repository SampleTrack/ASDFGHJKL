# plugins/my_trackings.py
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from helper.database import products, users

logger = logging.getLogger(__name__)

async def list_trackings_handler(client: Client, entity):
    """
    Displays the user's list of tracked products.
    This is a helper function intended to be called from both commands and callbacks.
    `entity` can be a Message or a CallbackQuery (message is then entity.message).
    """
    from pyrogram.types import CallbackQuery  # local import to avoid circular issues when callbacks import this file

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
        if isinstance(entity, CallbackQuery):
            await message.edit_text(text)
        else:
            await message.reply_text(text, quote=True)
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
        if isinstance(entity, CallbackQuery):
            await message.edit_text(text)
        else:
            await message.reply_text(text, quote=True)
        return

    if not product_docs:
        text = ("😔 **You are not tracking any products yet.**\n"
                "Looks like your previous trackings were removed. Send a new link to start!")
        if isinstance(entity, CallbackQuery):
            await message.edit_text(text)
        else:
            await message.reply_text(text, quote=True)
        return

    keyboard_buttons = []
    for doc in product_docs:
        product_name = doc.get('product_name', 'Unnamed Product')
        product_id = doc.get('_id')
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


# Command handler: /my_trackings (keeps the command in this file)
@Client.on_message(filters.command("my_trackings") & filters.private)
async def trackings_command_handler(client: Client, message: Message):
    """Handles the /my_trackings command."""
    await list_trackings_handler(client, message)
