
#code to save in utils
from pyrogram import enums
from config import Telegram

async def report_error(app, error_message: str):
    try:
        await app.send_message(
            chat_id=Telegram.ERROR_LOGGER_ID,
            text=f"**#Error :**\n{error_message}",
            reply_to_message_id=Telegram.ERROR_LOGGER_TOPIC,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        print(f"Failed to report error: {e}")
