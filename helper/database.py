from pymongo import MongoClient
import logging
from config import Telegram, Db

client = MongoClient(Db.MONGO_URI)

users = client[Db.DB_NAME]['users']
products = client[Db.DB_NAME]['products']

logging.basicConfig(
    level=logging.WARNING,
    format='[%(levelname)s/%(asctime)s] %(name)s:%(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def send_join_log(client, log_message):
    try:
        if Telegram.SEND_JOIN_LOG:
            # FIX: CHANNEL_ID was undefined. Used Telegram.LOG_CHANNEL_ID from config.
            await client.send_message(
                chat_id=Telegram.LOG_CHANNEL_ID,
                text=log_message
            )
    except Exception as e:
        logger.warning(f"Failed to send error log: {e}")


async def is_user_exist(user_id):
    # FIX: Removed 'await' because pymongo is synchronous
    user = users.find_one({"user_id": str(user_id)})
    return bool(user)


async def add_user(user_id, client):
    user = await client.get_users(user_id)
    first_name = user.first_name

    # FIX: Removed 'await' because pymongo is synchronous
    users.insert_one({
        "user_id": str(user_id),
        "first_name": first_name
    })

def remove_user(user_id):
    # FIX: 'already_db' was undefined. Added a direct sync check here.
    user = users.find_one({"user_id": str(user_id)})
    if not user:
        return 
    return users.delete_one({"user_id": str(user_id)})

def all_users():
    user = users.find({})
    usrs = len(list(user))
    return usrs
    
