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
            "no_history": "❌ Not enough data for a graph yet.",
            "view_details_btn": "👀 View Details",
            "buy_btn": "🔗 Buy Now",
            "remove_btn": "🗑️ Remove",
            "back_btn": "🔙 Back",
            "graph_btn": "📈 Graph"
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
            "no_history": "❌ ग्राफ के लिए पर्याप्त डेटा नहीं है।",
            "view_details_btn": "👀 विवरण देखें",
            "buy_btn": "🔗 अभी खरीदें",
            "remove_btn": "🗑️ हटाएं",
            "back_btn": "🔙 वापस",
            "graph_btn": "📈 ग्राफ"
        }
    }

    # Admin Texts (English only)
    STATS_TXT = """
📊 **Bot Usage Statistics**

👤 **Total Users:** `{users}`
🔗 **Total Active Trackings:** `{trackings}`

📈 **Trackings by Source (Active):**
{sources}

🏆 **Top 10 Users by Trackings:**
{top_users}

⏱️ Report generated in `{time}` seconds
"""

    STATUS_TXT = """
#{date} **Price Check Complete!**

📊 **Overall Summary:**
- Products Checked: `{checked}`
- Active Trackings: `{active_tr}`
- Users with Trackings: `{user_tr}`

📈 **Price Changes:**
- Increased: `{inc}` | Decreased: `{dec}`

🔍 **Per-Platform:**
{platforms}

🔔 **Price Notifications:**
- Unique Users Notified: `{uniq_users}`
- Total Sent: `{sent}` | Failed: `{failed}`

⚙️ **System Health:**
- API/Scraping Errors: `{errors}`

⏱️ **Performance:**
- Avg. Time per Product: `{avg_time}s`
- Total Time Taken: `{total_time}s`
"""
    
    # Keep Logs templates
    NEW_USER_LOG = "**#New_User**\n**User:** [{name}](tg://user?id={id})\n**ID:** `{id}`"
    RESTART_LOG = "**🔄 Bot Restarted**\n**Date:** `{date}`\n**Time:** `{time}`"
