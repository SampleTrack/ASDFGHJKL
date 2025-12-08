class Script:
    # Dictionary for Multi-Language Support
    # Usage: Script.STRINGS[lang_code]['key']
    STRINGS = {
        "en": {
            "start": "**👋 Hello {first_name}!**\n\nI am your **E-commerce Price Tracker Bot**. 📉\n\nSend me a link to start, or use the buttons below.",
            "help": "**ℹ️ How to Use:**\n\n1. Copy product link.\n2. Paste it here.\n3. I will track it.\n\nUse /lang to change language.",
            "about": "**🤖 About Me**\nVersion: v2.1 (Graph Support)",
            "tracking_started": "**✅ Tracking Started!**\n\n**Price:** {price}",
            "tracking_list": "**📋 Your Tracked Products:**",
            "empty_list": "🤷‍♂️ **Empty List**",
            "dropped": "📉 **Dropped:** {currency}{diff} ({percent}%) since added.",
            "increased": "📈 **Increased:** {currency}{diff} ({percent}%) since added.",
            "no_change": "➖ **No Change** since added.",
            "removed": "✅ Removed!",
            "fetching": "🔎 **Fetching details...**",
            "set_lang": "✅ Language set to **English** 🇺🇸",
            "graph_caption": "📊 **Price History for:** {name}",
            "no_history": "❌ Not enough data for a graph yet."
        },
        "hi": {
            "start": "**👋 नमस्ते {first_name}!**\n\nमैं आपका **Price Tracker Bot** हूँ। 📉\n\nअमेज़न/फ्लिपकार्ट का लिंक भेजें।",
            "help": "**ℹ️ कैसे उपयोग करें:**\n\n1. लिंक कॉपी करें।\n2. यहाँ पेस्ट करें।\n3. मैं ट्रैक करूँगा।\n\nभाषा बदलने के लिए /lang का उपयोग करें।",
            "about": "**🤖 मेरे बारे में**\nसंस्करण: v2.1",
            "tracking_started": "**✅ ट्रैकिंग शुरू!**\n\n**कीमत:** {price}",
            "tracking_list": "**📋 आपके प्रोडक्ट्स:**",
            "empty_list": "🤷‍♂️ **सूची खाली है**",
            "dropped": "📉 **गिरावट:** {currency}{diff} ({percent}%) जब से आपने जोड़ा।",
            "increased": "📈 **बढ़ोतरी:** {currency}{diff} ({percent}%) जब से आपने जोड़ा।",
            "no_change": "➖ **कोई बदलाव नहीं**",
            "removed": "✅ हटा दिया गया!",
            "fetching": "🔎 **विवरण लाया जा रहा है...**",
            "set_lang": "✅ भाषा **हिंदी** 🇮🇳 सेट की गई",
            "graph_caption": "📊 **कीमत इतिहास:** {name}",
            "no_history": "❌ ग्राफ के लिए पर्याप्त डेटा नहीं है।"
        }
    }

    # Admin Texts remain static (usually English)
    STATS_TXT = """
📊 **Bot Usage Statistics**

👤 **Total Users:** `{users}`
🔗 **Total Active Trackings:** `{trackings}`

📈 **Trackings by Source:**
{sources}

🏆 **Top 10 Users:**
{top_users}

⏱️ Report generated in `{time}` seconds
"""

    STATUS_TXT = """
#{date} **Price Check Complete!**

📊 **Overall Summary:**
- Products Checked: `{checked}`
- Price Changes Detected: `{changes}`

📈 **Price Changes:**
- Increased: `{inc}` | Decreased: `{dec}`

🔍 **Per-Platform:**
{platforms}

🔔 **Notifications:**
- Sent: `{sent}` | Failed: `{failed}`

⏱️ **Performance:**
- Total Time: `{total_time}s`
- Avg per Product: `{avg_time}s`
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
