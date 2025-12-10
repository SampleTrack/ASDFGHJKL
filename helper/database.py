
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
        await client.send_message(
          chat_id=CHANNEL_ID,
          text=log_message
        )
    except Exception as e:
        logger.warning(f"Failed to send error log: {e}")


def already_db(user_id):
    user = users.find_one({"user_id": str(user_id)})
    if not user:
        return False
    return True

async def add_user(user_id, client):
    in_db = already_db(user_id)
    if in_db:
        return
    user = await client.get_users(user_id)  # Await here
    first_name = user.first_name
    users.insert_one({"user_id": str(user_id)})        
    return await send_join_log(client, f"#New_User\n\nNew User\n\n [{first_name}]( tg://user?id={user_id})")

def remove_user(user_id):
    in_db = already_db(user_id)
    if not in_db:
        return 
    return users.delete_one({"user_id": str(user_id)})

def all_users():
    user = users.find({})
    usrs = len(list(user))
    return usrs
