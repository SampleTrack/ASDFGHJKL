import asyncio
import logging
import threading
from flask import Flask
from pyrogram import Client, idle
from config import Config
from Script import Script
from helper.database import db
from helper.utils import fetch_product_info
from datetime import datetime

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Flask Server
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    web_app.run(host="0.0.0.0", port=Config.PORT)

# Price Checker Logic
async def check_prices(app):
    logger.info("Starting Price Check Loop...")
    while True:
        try:
            products = db.products.find({})
            async for product in products:
                try:
                    url = product.get('url')
                    current_db_price = product.get('current_price', {}).get('int', 0)
                    
                    data = await fetch_product_info(url)
                    if not data or not data.get('dealsData'):
                        continue # Skip invalid API response
                        
                    api_prod = data['dealsData']['product_data']
                    currency = data.get('currencySymbol', '₹')
                    new_price_str = str(api_prod.get('cur_price', '0'))
                    
                    try:
                        new_price_int = int(float(new_price_str.replace(',', '').replace(currency, '').strip()))
                    except:
                        continue

                    # Compare Prices
                    if new_price_int != current_db_price and new_price_int > 0:
                        # Price Changed!
                        change_type = "dropped ⬇️" if new_price_int < current_db_price else "increased ⬆️"
                        
                        # Update DB
                        await db.update_product_price(product['_id'], new_price_str, new_price_int)
                        
                        # Notify Users
                        users_tracking = await db.users.find({"trackings": product['_id']}).to_list(length=None)
                        for user in users_tracking:
                            try:
                                msg = (f"**🚨 Price Alert!**\n\n"
                                       f"**{product['product_name']}** has {change_type}\n"
                                       f"**New Price:** {currency}{new_price_str}\n"
                                       f"[Check Now]({url})")
                                await app.send_message(user['user_id'], msg)
                                await asyncio.sleep(0.5) # Floodwait prevention
                            except Exception as e:
                                logger.error(f"Failed to notify {user['user_id']}: {e}")

                except Exception as inner_e:
                    logger.error(f"Error checking product {product.get('_id')}: {inner_e}")
                    
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        
        await asyncio.sleep(Config.CHECK_INTERVAL)

# Main Bot Start
app = Client(
    "PriceTracker",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

async def start_bot():
    await app.start()
    print("Bot Started!")
    
    # Send Restart Log
    if Config.LOG_CHANNEL:
        try:
            await app.send_message(
                Config.LOG_CHANNEL, 
                Script.RESTART_LOG.format(
                    date=datetime.now().strftime("%Y-%m-%d"),
                    time=datetime.now().strftime("%H:%M:%S")
                )
            )
            for admin in Config.ADMINS:
                await app.send_message(admin, "🤖 Bot has restarted!")
        except Exception as e:
            logger.error(f"Log Error: {e}")

    # Start Background Task
    asyncio.create_task(check_prices(app))
    
    await idle()
    await app.stop()

if __name__ == "__main__":
    # Start Flask in separate thread
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Start Bot
    app.loop.run_until_complete(start_bot())
