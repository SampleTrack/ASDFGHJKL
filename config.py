import os

class Telegram:
    # Use "0" as default for integers to prevent ValueError on empty strings
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    BOT_NICKNAME = os.getenv("BOT_NICKNAME", "")

    ADMIN = int(os.getenv("ADMIN", "0"))

    # Force Sub
    # Fixed typo: Fusb_name -> FSUB_NAME to match naming convention
    FSUB_NAME = os.getenv("Fusb_name", "@botio_devs")
    FSUB_ID = int(os.getenv("Fsub_ID", "-1002054575318"))
    FSUB_LINK = os.getenv("Fsub_Link", "https://t.me/+9Mxv8UvcoPw0MjA9")

    # LOGGING
    SEND_JOIN_LOG = True
    LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "-1001914822368"))
    
    # Assigning the same ID to multiple variables
    JOIN_LOG_CHANNEL = LOG_CHANNEL_ID
    ERROR_LOGGER_ID = LOG_CHANNEL_ID
    CHANNEL_ID = LOG_CHANNEL_ID

    CHECKER_LOG_TOPIC = 3
    ERROR_LOGGER_TOPIC = 38

    # Button Links
    UPDATES_CHANNEL = "https://t.me/botio_devs"
    SUPPORT_CHANNEL = "https://t.me/botio_devs_discuss"


class Db:
    MONGO_URI = os.getenv("MONGO_URI", "your mongo uri")
    DB_NAME = "ecom-tracker"


class Server:
    PORT = 8080
    # Best practice for Env booleans: Check if the string equals "true"
    IS_SERVER = os.getenv("IS_SERVER", "False").lower() == "true"
