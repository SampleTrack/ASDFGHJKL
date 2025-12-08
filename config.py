import os

class Config:
    # Get these from my.telegram.org
    API_ID = int(os.getenv("API_ID", "12345"))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    
    # Bot Token from @BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # Admins
    admin_str = os.getenv("ADMINS", "")
    ADMINS = [int(x) for x in admin_str.replace(",", " ").split()] if admin_str else []

    # Database
    DB_URL = os.getenv("DB_URL", "") 
    DB_NAME = os.getenv("DB_NAME", "PriceTrackerBot")

    # Logging
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0")) 
    
    # Server
    PORT = int(os.getenv("PORT", "8080"))
    
    # UPDATED: Check every 2 Hours (7200 seconds)
    CHECK_INTERVAL = 7200 

    # NEW: Global Variable to store the results of the last background check
    LAST_CHECK_STATS = {
        "status": "Not run yet",
        "data": None
    }
