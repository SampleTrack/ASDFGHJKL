import os

class Config:
    # Get these from my.telegram.org
    API_ID = int(os.getenv("API_ID", "12345"))
    API_HASH = os.getenv("API_HASH", "your_api_hash")
    
    # Bot Token from @BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # Admins: Can be a single ID or list separated by spaces/commas
    admin_str = os.getenv("ADMINS", "")
    ADMINS = [int(x) for x in admin_str.replace(",", " ").split()] if admin_str else []

    # Database
    DB_URL = os.getenv("DB_URL", "") # MongoDB Connection String
    DB_NAME = os.getenv("DB_NAME", "PriceTrackerBot")

    # Logging
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0")) # Channel ID (starts with -100)
    
    # Server
    PORT = int(os.getenv("PORT", "8080"))
    
    # Sleep time for price checker (in seconds)
    CHECK_INTERVAL = 18000 # 5 Hours
