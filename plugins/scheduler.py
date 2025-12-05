import asyncio
import logging
from config import Config
from database import db
from helpers.scraper import fetch_product_details

logger = logging.getLogger(__name__)

async def check_prices(client):
    logger.info("Starting Price Check Job...")
    all_products = db.get_all_products()
    
    if not all_products:
        logger.info("No products to check.")
        return

    for product in all_products:
        try:
            # Add delay to respect API limits
            await asyncio.sleep(2) 
            
            new_data, error = await fetch_product_details(product['url'])
            if error or not new_data:
                continue
            
            old_price = product.get('current_price', 0)
            new_price = new_data['current_price']
            
            # If price changed
            if new_price != old_price:
                db.update_product_price(product['_id'], new_data)
                
                # Notify Users
                users_to_notify = db.get_users_tracking_product(product['_id'])
                
                change_type = "📉 Price Dropped!" if new_price < old_price else "📈 Price Increased!"
                msg = (
                    f"**{change_type}**\n\n"
                    f"**Product:** [{new_data['name']}]({new_data['url']})\n"
                    f"**Old Price:** {old_price}\n"
                    f"**New Price:** {new_price}"
                )
                
                for user in users_to_notify:
                    try:
                        await client.send_message(user['user_id'], msg)
                    except Exception as e:
                        logger.error(f"Failed to notify {user['user_id']}: {e}")
                        
        except Exception as e:
            logger.error(f"Error checking product {product.get('_id')}: {e}")

    logger.info("Price Check Job Completed.")

async def start_scheduler(client):
    # Check every 4 hours (14400 seconds)
    while True:
        await check_prices(client)
        await asyncio.sleep(14400)
