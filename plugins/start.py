import os, random, asyncio
from pyrogram import Client as app, filters, types, enums, errors
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, FloodWait, UserDeactivated, UserIsBlocked

# Local imports
from config import Telegram
from helper.database import add_user, all_users, users, remove_user
from helper.message_text import text_messages, message_buttons


@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    try:
        await client.get_chat_member(Telegram.Fsub_ID, user_id)
        await add_user(user_id, client)
        await message.reply_text(
            text_messages.start_text,
            disable_web_page_preview=True,
            reply_to_message_id=message.id,
            reply_markup=message_buttons.start_buttons,
        )
    except UserNotParticipant:
        await message.reply(
            text_messages.Fsub_text,
            reply_markup=message_buttons.Fsub_buttons
        )
    except Exception as e:
        print(f"Error in start function: {e}")


@app.on_message(filters.command("help"))
async def help_command(client, msg: types.Message):
    """Reply help message"""
    try:
        await msg.reply(
            text_messages.help_text,
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    except Exception as e:
        print(f"Error in help: {e}")
        await msg.reply("An error occurred. Please try again later.")


@app.on_message(filters.command("users") & filters.user(Telegram.ADMIN))
async def dbtool(client, message):
    xx = all_users()
    await message.reply(f"""
🍀 Chats Stats 🍀
🙋‍♂️ Users : `{xx}` """)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Broadcast Copy ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.command("bcast") & filters.user(Telegram.ADMIN))
async def bcast(_, m: Message):
    if not m.reply_to_message:
        await m.reply_text("❌ Please reply to a message to broadcast it.")
        return

    allusers = users
    lel = await m.reply_text("`⚡️ Processing...`")

    success = failed = deactivated = blocked = 0

    for count, usrs in enumerate(allusers.find(), start=1):
        userid = usrs.get("user_id")
        try:
            await m.reply_to_message.copy(int(userid))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await m.reply_to_message.copy(int(userid))
            success += 1
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(userid)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(f"Failed to send to {userid}: {e}")
            failed += 1

        # 🔄 Update every 50 users
        if count % 50 == 0:
            try:
                await lel.edit(
                    f"📢 Broadcasting...\n"
                    f"✅ Sent: `{success}`\n"
                    f"❌ Failed: `{failed}`\n"
                    f"👾 Blocked: `{blocked}`\n"
                    f"👻 Deactivated: `{deactivated}`\n"
                    f"📊 Processed: `{count}` users"
                )
            except Exception:
                pass

    # ✅ Final result
    await lel.edit(
        f"✅ Successfully sent to `{success}` users.\n"
        f"❌ Failed to send to `{failed}` users.\n"
        f"👾 Found `{blocked}` blocked users\n"
        f"👻 Found `{deactivated}` deactivated users."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Broadcast Forward ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@app.on_message(filters.command("fcast") & filters.user(Telegram.ADMIN))
async def fcast(_, m: Message):
    if not m.reply_to_message:
        await m.reply_text("❌ Please reply to a message to forward-broadcast it.")
        return

    allusers = users
    lel = await m.reply_text("`⚡️ Processing...`")

    success = failed = deactivated = blocked = 0

    for count, usrs in enumerate(allusers.find(), start=1):
        userid = usrs.get("user_id")
        try:
            await m.reply_to_message.forward(int(userid))
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await m.reply_to_message.forward(int(userid))
            success += 1
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(userid)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(f"Failed to forward to {userid}: {e}")
            failed += 1

        # 🔄 Update every 50 users
        if count % 50 == 0:
            try:
                await lel.edit(
                    f"📢 Forwarding...\n"
                    f"✅ Forwarded: `{success}`\n"
                    f"❌ Failed: `{failed}`\n"
                    f"👾 Blocked: `{blocked}`\n"
                    f"👻 Deactivated: `{deactivated}`\n"
                    f"📊 Processed: `{count}` users"
                )
            except Exception:
                pass

    # ✅ Final result
    await lel.edit(
        f"✅ Successfully forwarded to `{success}` users.\n"
        f"❌ Failed to forward to `{failed}` users.\n"
        f"👾 Found `{blocked}` blocked users \n"
        f"👻 Found `{deactivated}` deactivated users."
    )
