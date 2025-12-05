import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Get these from my.telegram.org
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    
    # Get this from @BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # MongoDB Connection String
    MONGO_URI = os.getenv("MONGO_URI", "")
    DB_NAME = "PriceTrackerBot"
    
    # Admin User ID (Integer)
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
    
    # ID of the Channel to send logs/suggestions to (Start with -100)
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
    
    # External API for tracking (Do not change unless you have a replacement)
    TRACKER_API = "https://e-com-price-tracker-lemon.vercel.app/buyhatke"
    
    # Web Server Config
    PORT = int(os.getenv("PORT", "8080"))
