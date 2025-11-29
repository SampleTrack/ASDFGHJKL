import os
import re

# === BASIC CONFIG === #
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_NAME = os.getenv("BOT_NAME", "")

ADMINS = int(os.getenv("ADMINS", "0"))

# === FORCE SUB SETTINGS === #
FUSB_NAME = os.getenv("FUSB_NAME", "@botio_devs")
FSUB_ID = int(os.getenv("FSUB_ID", "-1002054575318"))
FSUB_LINK = os.getenv("FSUB_LINK", "https://t.me/+9Mxv8UvcoPw0MjA9")

# === LOGGING === #
SEND_JOIN_LOG = True
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "0"))

JOIN_LOG_CHANNEL = LOG_CHANNEL
ERROR_LOGGER_ID = LOG_CHANNEL
CHANNEL_ID = LOG_CHANNEL

CHECKER_LOG_TOPIC = 3
ERROR_LOGGER_TOPIC = 38

# === BUTTON LINKS === #
UPDATES_CHANNEL = "https://t.me/botio_devs"
SUPPORT_CHANNEL = "https://t.me/botio_devs_discuss"

# === DATABASE === #
DATABASE_URL = os.environ.get('DATABASE_URL', "")
DATABASE_NAME = os.getenv('DATABASE_NAME', "")

# === SERVER SETTINGS === #
PORT = int(os.environ.get("PORT", 8080))
IS_SERVER = os.getenv("IS_SERVER", "TRUE").lower() == "true"
