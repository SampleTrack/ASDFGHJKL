class Script:
    START_TXT = """
**👋 Hello {first_name}!**

I am your **E-commerce Price Tracker Bot**. 📉

I track **Amazon** and **Flipkart** prices for you.
Send me a link to start, or use the buttons below to manage your items.
"""

    HELP_TXT = """
**ℹ️ How to Use:**

1. **Copy Link:** Copy a product URL from Amazon/Flipkart.
2. **Send Link:** Paste it here.
3. **Track:** I will auto-detect it.

**Manage Trackings:**
Click **"📦 My Trackings"** to see your list. You can remove items there.
"""

    ABOUT_TXT = """
**🤖 About Me**

**Name:** Price Tracker Bot
**Version:** v2.0 (Async)
**Dev:** BotIO Devs
**Language:** Python 3 (Pyrogram)
**Database:** MongoDB (Motor)

__Keeping your wallet safe since 2025.__
"""

    # Keep your existing STATS_TXT, BAN_TXT, etc.
    STATS_TXT = """
**📊 Admin Statistics**

**👥 Total Users:** `{users}`
**📅 Users Today:** `{today}`
**📦 Total Tracked Products:** `{products}`
**📉 Storage Used:** `{storage}`
"""
    BAN_TXT = "🚫 **You are banned.**"
    
    NEW_USER_LOG = """
**#New_User**
**User:** [{name}](tg://user?id={id})
**ID:** `{id}`
**Date:** `{date}`
"""

    RESTART_LOG = """
**🔄 Bot Restarted**
**Date:** `{date}`
**Time:** `{time}`
"""
