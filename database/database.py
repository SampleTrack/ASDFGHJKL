import motor.motor_asyncio
from config import DATABASE_NAME, DATABASE_URL


class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.products = self.db.products

    def new_user(self, id, name):
        return {
            "id": id,
            "name": name,
            "ban_status": {
                "is_banned": False,
                "ban_reason": ""
            },
        }

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return bool(user)

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def remove_ban(self, id):
        ban_status = {
            "is_banned": False,
            "ban_reason": ""
        }
        await self.col.update_one({"id": id}, {"$set": {"ban_status": ban_status}})

    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = {
            "is_banned": True,
            "ban_reason": ban_reason
        }
        await self.col.update_one({"id": user_id}, {"$set": {"ban_status": ban_status}})

    async def get_ban_status(self, id):
        default = {
            "is_banned": False,
            "ban_reason": ""
        }
        user = await self.col.find_one({"id": int(id)})
        if not user:
            return default
        return user.get("ban_status", default)

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})

    async def get_banned(self):
        cursor = self.col.find({"ban_status.is_banned": True})
        banned_users = [user["id"] async for user in cursor]
        return banned_users

    async def get_db_size(self):
        stats = await self.db.command("dbstats")
        return stats["dataSize"]


db = Database(DATABASE_URL, DATABASE_NAME)
