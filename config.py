import os

class Telegram():
    # FIX: Added default '0' to prevent crash if env var is empty
    API_ID = int(os.getenv("API_ID", 0)) 
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    BOT_NICKNAME = os.getenv("BOT_NICKNAME", "")
    
    # FIX: Added default '0'
    ADMIN = int(os.getenv("ADMIN", 0))     

    # Force Sub
    # FIX: Corrected variable name spelling if needed, handled defaults
    Fusb_name = os.getenv("Fusb_name", "@botio_devs")
    Fsub_ID = int(os.getenv("Fsub_ID", 0))     
    Fsub_Link = os.getenv("Fsub_Link", "https://t.me/+9Mxv8UvcoPw0MjA9")

    # LOGGING
    SEND_JOIN_LOG = True
    # FIX: Added default '0'
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0))
    JOIN_LOG_CHANNEL = ERROR_LOGGER_ID = CHANNEL_ID = LOG_CHANNEL_ID
    
    CHECKER_LOG_TOPIC = 3
    ERROR_LOGGER_TOPIC = 38
    
    # Button Link
    UPDATES_CHANNEL = "https://t.me/botio_devs"
    SUPPORT_CHANNEL = "https://t.me/botio_devs_discuss" 

class Db():
    MONGO_URI = os.getenv("MONGO_URI", "your mongo uri") 
    DB_NAME = "ecom-tracker"

class Server():
    PORT = 8080
    IS_SERVER = os.getenv("IS_SERVER", False)
  
