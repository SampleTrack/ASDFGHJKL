class Script:
    START_TXT = """
**👋 Hello {first_name}!**

I am an advanced **E-commerce Price Tracker Bot**. 📉

I can track prices for products on **Amazon** and **Flipkart**.
Just send me a product link, and I will notify you when the price drops! 🔔

**Commands:**
/trackings - View your tracked items
/help - How to use me
"""

    HELP_TXT = """
**ℹ️ How to Use:**

1. **Copy Link:** Go to Amazon or Flipkart and copy the product link.
2. **Send Link:** Paste the link here.
3. **Track:** Click the 'Start Tracking' button.

**Manage Trackings:**
Use /trackings to view or delete items you are watching.

**Support:**
Contact: @YourSupportHandle
"""

    ABOUT_TXT = """
**🤖 Name:** Price Tracker Bot
**📢 Channel:** [Updates Channel](https://t.me/YourChannel)
**👨‍💻 Dev:** [Developer](https://t.me/YourDev)
**📚 Language:** Python 3 (Pyrogram)
**🗄️ Database:** MongoDB (Motor)
"""

    STATS_TXT = """
**📊 Bot Statistics**

**👥 Total Users:** `{users}`
**📅 Users Today:** `{today}`
**📦 Total Tracked Products:** `{products}`
**📉 Storage Used:** `{storage}`
"""

    BAN_TXT = "🚫 **You are banned from using this bot.**"
    
    # Logger Texts
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
