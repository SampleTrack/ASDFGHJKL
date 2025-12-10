from config import Telegram
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

class text_messages():
  start_text = """
**𝒲𝑒𝓁𝒸𝑜𝓂𝑒 𝓉𝑜 𝒫𝓇𝒾𝒸𝑒 𝒯𝓇𝒶𝒸𝓀𝑒𝓇 𝐵𝑜𝓉!

ᴇᴀꜱɪʟʏ ᴛʀᴀᴄᴋ ᴘʀɪᴄᴇꜱ ᴏꜰ ʏᴏᴜʀ ꜰᴀᴠᴏʀɪᴛᴇ ᴘʀᴏᴅᴜᴄᴛꜱ ꜰʀᴏᴍ ᴀᴍᴀᴢᴏɴ 🛒 ᴀɴᴅ ꜰʟɪᴘᴋᴀʀᴛ 📦.

**--🔍 ᴊᴜꜱᴛ ꜱᴇɴᴅ ᴍᴇ ᴀ ᴘʀᴏᴅᴜᴄᴛ ʟɪɴᴋ, ᴀɴᴅ ɪ’ʟʟ:--**

📉 ᴛʀᴀᴄᴋ ᴘʀɪᴄᴇ ᴄʜᴀɴɢᴇꜱ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ
🔔 ɴᴏᴛɪꜰʏ ʏᴏᴜ ᴡʜᴇɴ ᴛʜᴇ ᴘʀɪᴄᴇ ᴅʀᴏᴘꜱ
📊 ꜱʜᴏᴡ ᴘʀᴏᴅᴜᴄᴛ ᴅᴇᴛᴀɪʟꜱ & ᴄᴜʀʀᴇɴᴛ ᴘʀɪᴄᴇ
✨ ꜱᴛᴀʏ ᴀʜᴇᴀᴅ ᴏꜰ ᴅᴇᴀʟꜱ ᴀɴᴅ ɴᴇᴠᴇʀ ᴍɪꜱꜱ ᴀ ᴅɪꜱᴄᴏᴜɴᴛ!

**ᑭOᗯEᖇEᗪ ᗷY @BOTIO_DEVS**
"""

#----
  
  help_text = """
--**ℹ️ 𝙷𝚘𝚠 𝚝𝚘 𝚄𝚜𝚎 𝙿𝚛𝚒𝚌𝚎 𝚃𝚛𝚊𝚌𝚔𝚎𝚛 𝙱𝚘𝚝⁉️**--

**--1️⃣ ꜱᴛᴀʀᴛ ᴛʀᴀᴄᴋɪɴɢ--**

**​🇸​​🇪​​🇳​​🇩​ ​🇲​​🇪​ ​🇦​​🇳​​🇾​ ​🇦​​🇲​​🇦​​🇿​​🇴​​🇳​ 🛒 ​🇴​​🇷​ ​🇫​​🇱​​🇮​​🇵​​🇰​​🇦​​🇷​​🇹​ 📦 ​🇵​​🇷​​🇴​​🇩​​🇺​​🇨​​🇹​ ​🇱​​🇮​​🇳​​🇰​.
🇨​​🇱​​🇮​​🇨​​🇰​ ​🇴​​🇳​ ​🇸​​🇹​​🇦​​🇷​​🇹​ ​🇹​​🇷​​🇦​​🇨​​🇰​​🇮​​🇳​​🇬​ ​🇹​​🇴​ ​🇧​​🇪​​🇬​​🇮​​🇳​ ​🇹​​🇷​​🇦​​🇨​​🇰​​🇮​​🇳​​🇬​ ​🇹​​🇭​​🇪​ ​🇵​​🇷​​🇴​​🇩​​🇺​​🇨​​🇹​’​🇸​ ​🇵​​🇷​​🇮​​🇨​​🇪​.**

--**2️⃣ ᴠɪᴇᴡ ʏᴏᴜʀ ᴛʀᴀᴄᴋɪɴɢꜱ--**

**ᴜꜱᴇ /my_trackings ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴛʜᴇ ᴘʀᴏᴅᴜᴄᴛꜱ ʏᴏᴜ’ʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴛʀᴀᴄᴋɪɴɢ.**

**--3️⃣ ʀᴇᴍᴏᴠᴇ ᴛʀᴀᴄᴋɪɴɢ--**

**ꜰʀᴏᴍ ʏᴏᴜʀ ᴛʀᴀᴄᴋɪɴɢꜱ ʟɪꜱᴛ, ʏᴏᴜ ᴄᴀɴ ʀᴇᴍᴏᴠᴇ ᴘʀᴏᴅᴜᴄᴛꜱ ʏᴏᴜ ɴᴏ ʟᴏɴɢᴇʀ ᴡᴀɴᴛ ᴛᴏ ᴛʀᴀᴄᴋ.**


**--📢 ꜱᴜᴘᴘᴏʀᴛ & ɪꜱꜱᴜᴇꜱ--**

ꜰᴏʀ ᴅᴏᴜʙᴛꜱ, Qᴜᴇꜱᴛɪᴏɴꜱ, ᴏʀ ʙᴜɢ ʀᴇᴘᴏʀᴛꜱ, ᴊᴏɪɴ: @ʙᴏᴛɪᴏ_ᴅᴇᴠꜱ_ᴅɪꜱᴄᴜꜱꜱ

ꜱᴛᴀʏ ᴜᴘᴅᴀᴛᴇᴅ, ꜱᴀᴠᴇ ᴍᴏɴᴇʏ 💰, ᴀɴᴅ ɴᴇᴠᴇʀ ᴍɪꜱꜱ ᴀ ᴅᴇᴀʟ! 🚀
𝒮𝓉𝒶𝓎 𝓊𝓅𝒹𝒶𝓉𝑒𝒹, 𝓈𝒶𝓋𝑒 𝓂𝑜𝓃𝑒𝓎 💰, 𝒶𝓃𝒹 𝓃𝑒𝓋𝑒𝓇 𝓂𝒾𝓈𝓈 𝒶 𝒹𝑒𝒶𝓁! 🚀

"""
  Fsub_text = f"**⚠️Access Denied!⚠️\n\nPlease Join [{Telegram.Fusb_name}]({Telegram.Fsub_Link}) to use me. If you joined click check again button to confirm.**"

  verification_text = """
**Sorry! 🥺🥹**   
To cover costs and prevent abuse, you'll need **access** to use me.  

🎉 **Get Unlimited Access Today!**  
Unlock **all 20 bots** with **no ad-limits** until **11:59 PM** by completing a quick step.  

👇 **Tap the button below to get your access link!**  

💬 For issues, reach us at [@botio_devs_discuss](https://t.me/botio_devs_discuss).  
✨ **Enjoy seamless bot access!**
"""

class message_buttons():
  Fsub_buttons = InlineKeyboardMarkup(
    [
      [InlineKeyboardButton("🍀join 🍀", url=Telegram.Fsub_Link)]
    ]
  )

  start_buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("UPDATES", url=Telegram.UPDATES_CHANNEL),
            InlineKeyboardButton("SUPPORT", url=Telegram.SUPPORT_CHANNEL)
        ],
        [
            InlineKeyboardButton("ABOUT", callback_data="about")
        ]
    ])

  verification_button = [[
            InlineKeyboardButton("👨‍💻 ᴠᴇʀɪғʏ", url="https://t.me/Bots_Access_Manager_l_Bot?start=terabox")
        ]]
