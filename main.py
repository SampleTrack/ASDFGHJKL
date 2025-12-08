import asyncio
import logging
import threading
import time
from flask import Flask
from pyrogram import Client, idle
from config import Config
from Script import Script
from helper.database import db
from helper.utils import fetch_product_info
from datetime import datetime

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()])
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Running!"
def run_flask(): web_app.run(host="0.0.0.0", port=Config.PORT)

# --- ADVANCED PRICE CHECKER ---
async def check_prices(app):
    await asyncio.sleep(30)
    logger.info("Starting Price Check Loop...")
    
    while True:
        start_time = time.time()
        stats = {
            "checked": 0, "changes": 0, "inc": 0, "dec": 0, 
            "sent": 0, "failed": 0, "errors": 0,
            "unique_users_notified": 0,
            "platforms": {} 
        }
        notified_users = set()

        try:
            products = db.products.find({})
            async for product in products:
                stats["checked"] += 1
                source = product.get('source', 'Unknown')
                if source not in stats["platforms"]: stats["platforms"][source] = {"checked": 0, "drops": 0}
                stats["platforms"][source]["checked"] += 1

                try:
                    url = product.get('url')
                    current_db_price = product.get('current_price', {}).get('int', 0)
                    
                    data = await fetch_product_info(url)
                    if not data or not data.get('dealsData'):
                        stats["errors"] += 1
                        continue 
                        
                    api_prod = data['dealsData']['product_data']
                    currency = data.get('currencySymbol', '₹')
                    new_price_str = str(api_prod.get('cur_price', '0'))
                    try: new_price_int = int(float(new_price_str.replace(',', '').replace(currency, '').strip()))
                    except: continue

                    if new_price_int != current_db_price and new_price_int > 0:
                        stats["changes"] += 1
                        if new_price_int < current_db_price:
                            stats["dec"] += 1
                            stats["platforms"][source]["drops"] += 1
                            change_type = "dropped ⬇️"
                        else:
                            stats["inc"] += 1
                            change_type = "increased ⬆️"
                        
                        await db.update_product_price(product['_id'], new_price_str, new_price_int)
                        
                        # Notify
                        cursor = db.users.find({"trackings.id": product['_id']})
                        async for user in cursor:
                            try:
                                msg = (f"**🚨 Price Alert!**\n\n"
                                       f"**{product['product_name']}** has {change_type}\n"
                                       f"**New Price:** {currency}{new_price_str}\n"
                                       f"[Check Now]({url})")
                                await app.send_message(user['user_id'], msg, quote=True)
                                stats["sent"] += 1
                                notified_users.add(user['user_id'])
                                await asyncio.sleep(0.5) 
                            except Exception as e:
                                stats["failed"] += 1
                                logger.error(f"Notify fail: {e}")

                except Exception as inner_e:
                    stats["errors"] += 1
                    logger.error(f"Prod Error: {inner_e}")
                    
        except Exception as e:
            logger.error(f"Loop Error: {e}")
        
        end_time = time.time()
        stats["unique_users_notified"] = len(notified_users)
        
        # Save Global Stats
        Config.LAST_CHECK_STATS = {
            "status": "Success",
            "date": datetime.now().strftime("%b%d"),
            "data": stats,
            "perf": {"total": round(end_time - start_time, 2), 
                     "avg": round((end_time - start_time) / stats["checked"], 2) if stats["checked"] > 0 else 0}
        }
        
        logger.info(f"Check finished. Waiting {Config.CHECK_INTERVAL}s.")
        await asyncio.sleep(Config.CHECK_INTERVAL)

app = Client("PriceTracker", api_id=Config.API_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN, plugins=dict(root="plugins"))

async def start_bot():
    await app.start()
    print("Bot Started!")
    if Config.LOG_CHANNEL:
        await app.send_message(Config.LOG_CHANNEL, "**🤖 Bot Started** with Graph & Stats Support!", quote=True)
    asyncio.create_task(check_prices(app))
    await idle()
    await app.stop()

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app.loop.run_until_complete(start_bot())
