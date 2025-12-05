from pymongo import MongoClient
from config import Config
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]
        self.users = self.db['users']
        self.products = self.db['products']

    def add_user(self, user_id, first_name):
        if not self.users.find_one({"user_id": user_id}):
            self.users.insert_one({"user_id": user_id, "first_name": first_name, "trackings": []})
            return True
        return False

    def get_user(self, user_id):
        return self.users.find_one({"user_id": user_id})

    def get_all_users(self):
        return list(self.users.find())

    def add_tracking(self, user_id, product_data):
        product_id = product_data['_id']
        
        # Add to products collection if not exists (or update)
        self.products.update_one(
            {"_id": product_id}, 
            {"$set": product_data}, 
            upsert=True
        )
        
        # Add reference to user
        self.users.update_one(
            {"user_id": user_id},
            {"$addToSet": {"trackings": product_id}}
        )

    def remove_tracking(self, user_id, product_id):
        self.users.update_one(
            {"user_id": user_id},
            {"$pull": {"trackings": product_id}}
        )
        # We don't remove from products collection immediately to preserve history for other users

    def get_tracked_products(self, user_id):
        user = self.users.find_one({"user_id": user_id})
        if not user or not user.get('trackings'):
            return []
        
        tracking_ids = user['trackings']
        return list(self.products.find({"_id": {"$in": tracking_ids}}))

    def get_all_products(self):
        return list(self.products.find())

    def update_product_price(self, product_id, new_data):
        self.products.update_one({"_id": product_id}, {"$set": new_data})

    def get_users_tracking_product(self, product_id):
        return list(self.users.find({"trackings": product_id}))

db = Database()
