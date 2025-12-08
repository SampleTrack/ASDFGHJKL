import datetime
import motor.motor_asyncio
from config import Config

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.users
        self.products = self.db.products

    # --- User Functions ---
    async def add_user(self, user_id, name):
        user = await self.users.find_one({"user_id": int(user_id)})
        if not user:
            await self.users.insert_one({
                "user_id": int(user_id),
                "name": name,
                "lang": "en", # Default Language
                "banned": False,
                "joined_date": datetime.datetime.now(),
                "trackings": []
            })
            return True 
        return False 

    async def get_user(self, user_id):
        return await self.users.find_one({"user_id": int(user_id)})

    async def set_lang(self, user_id, lang_code):
        await self.users.update_one({"user_id": int(user_id)}, {"$set": {"lang": lang_code}})

    async def get_lang(self, user_id):
        user = await self.users.find_one({"user_id": int(user_id)})
        return user.get("lang", "en") if user else "en"

    async def get_all_users(self):
        return self.users.find({})

    async def total_users_count(self):
        return await self.users.count_documents({})
        
    async def get_active_trackings_count(self):
        # Counts users who have at least 1 item in trackings
        return await self.users.count_documents({"trackings.0": {"$exists": True}})

    async def get_top_users(self, limit=10):
        # Advanced Aggregation to count trackings array size
        pipeline = [
            {"$project": {
                "user_id": 1,
                "name": 1,
                "tracking_count": {"$size": {"$ifNull": ["$trackings", []]}}
            }},
            {"$sort": {"tracking_count": -1}},
            {"$limit": limit}
        ]
        return await self.users.aggregate(pipeline).to_list(length=limit)

    async def ban_user(self, user_id):
        await self.users.update_one({"user_id": int(user_id)}, {"$set": {"banned": True}})

    async def unban_user(self, user_id):
        await self.users.update_one({"user_id": int(user_id)}, {"$set": {"banned": False}})

    async def is_banned(self, user_id):
        user = await self.users.find_one({"user_id": int(user_id)})
        return user.get("banned", False) if user else False

    # --- Product Functions ---
    async def add_product(self, product_data):
        # Initialize price history with the starting price
        if "price_history" not in product_data:
            product_data["price_history"] = [{
                "date": datetime.datetime.now(), 
                "price": product_data['current_price']['int']
            }]
        await self.products.insert_one(product_data)

    async def get_product(self, product_id):
        return await self.products.find_one({"_id": product_id})
    
    async def update_product_price(self, product_id, new_price, new_price_int):
        # Push new price to history array and update current price
        history_obj = {
            "date": datetime.datetime.now(),
            "price": new_price_int
        }
        await self.products.update_one(
            {"_id": product_id},
            {
                "$set": {
                    "current_price.string": new_price, 
                    "current_price.int": new_price_int,
                    "last_checked": datetime.datetime.now()
                },
                "$push": {"price_history": history_obj}
            }
        )

    async def count_products_by_source(self):
        # Aggregation to count products per site (Amazon, Flipkart, etc)
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}}
        ]
        return await self.products.aggregate(pipeline).to_list(length=None)

    # --- User Tracking Functions ---
    async def add_tracking_to_user(self, user_id, product_id, current_price_int):
        await self.users.update_one(
            {"user_id": int(user_id)},
            {"$pull": {"trackings": {"id": product_id}}}
        )
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
        await self.users.update_one(
            {"user_id": int(user_id)},
            {"$pull": {"trackings": {"id": product_id}}}
        )
        is_tracked = await self.users.find_one({"trackings.id": product_id})
        if not is_tracked:
            await self.products.delete_one({"_id": product_id})

db = Database(Config.DB_URL, Config.DB_NAME)






