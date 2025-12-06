import datetime
import motor.motor_asyncio
from config import Config

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.users
        self.products = self.db.products

    async def add_user(self, user_id, name):
        user = await self.users.find_one({"user_id": int(user_id)})
        if not user:
            await self.users.insert_one({
                "user_id": int(user_id),
                "name": name,
                "banned": False,
                "joined_date": datetime.datetime.now(),
                "trackings": []
            })
            return True # New user
        return False # Existing user

    async def is_user_exist(self, user_id):
        user = await self.users.find_one({"user_id": int(user_id)})
        return bool(user)

    async def get_user(self, user_id):
        return await self.users.find_one({"user_id": int(user_id)})

    async def get_all_users(self):
        return self.users.find({})

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def get_daily_users(self):
        # Calculate users joined in the last 24 hours
        start_date = datetime.datetime.now() - datetime.timedelta(days=1)
        return await self.users.count_documents({"joined_date": {"$gte": start_date}})

    async def ban_user(self, user_id):
        await self.users.update_one({"user_id": int(user_id)}, {"$set": {"banned": True}})

    async def unban_user(self, user_id):
        await self.users.update_one({"user_id": int(user_id)}, {"$set": {"banned": False}})

    async def is_banned(self, user_id):
        user = await self.users.find_one({"user_id": int(user_id)})
        return user.get("banned", False) if user else False

    # Product Functions
    async def add_product(self, product_data):
        await self.products.insert_one(product_data)

    async def get_product(self, product_id):
        return await self.products.find_one({"_id": product_id})
    
    async def update_product_price(self, product_id, new_price, new_price_int):
        await self.products.update_one(
            {"_id": product_id},
            {"$set": {
                "current_price.string": new_price, 
                "current_price.int": new_price_int,
                "last_checked": datetime.datetime.now()
            }}
        )

    

    # ... inside class Database ...

    async def add_tracking_to_user(self, user_id, product_id, current_price_int):
        """
        Adds a product to the user's tracking list with the PRICE at that moment.
        """
        # 1. First, remove if it already exists (to update the price or prevent duplicates)
        await self.users.update_one(
            {"user_id": int(user_id)},
            {"$pull": {"trackings": {"id": product_id}}}
        )
        
        # 2. Add the new tracking object
        tracking_obj = {
            "id": product_id,
            "added_price": current_price_int,
            "date": datetime.datetime.now()
        }
        
        await self.users.update_one(
            {"user_id": int(user_id)},
            {"$push": {"trackings": tracking_obj}}
        )

    async def delete_product_tracking(self, user_id, product_id):
        # Remove the specific object where 'id' matches product_id
        await self.users.update_one(
            {"user_id": int(user_id)},
            {"$pull": {"trackings": {"id": product_id}}}
        )
        
        # Check if anyone else is tracking this product
        # Query changes to look inside the array of objects: "trackings.id"
        is_tracked = await self.users.find_one({"trackings.id": product_id})
        if not is_tracked:
            await self.products.delete_one({"_id": product_id})

db = Database(Config.DB_URL, Config.DB_NAME)
