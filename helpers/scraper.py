import httpx
import logging
from config import Config
import random
import string

logger = logging.getLogger(__name__)

def generate_id(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def fetch_product_details(url: str):
    """
    Fetches product details using the external API.
    """
    params = {"product_url": url}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(Config.TRACKER_API, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                return None, data.get("error")
                
            product_info = data.get("dealsData", {}).get("product_data")
            if not product_info:
                return None, "Could not parse product data."

            # Normalize Price
            try:
                price_str = str(product_info.get("cur_price", "0")).replace(",", "")
                current_price = int(float(price_str))
            except ValueError:
                current_price = 0

            return {
                "name": product_info.get("name"),
                "current_price": current_price,
                "original_price": product_info.get("orgi_price"),
                "discount": product_info.get("discount"),
                "image": product_info.get("thumbnailImages", [""])[0],
                "url": url,
                "source": product_info.get("site_name", "Unknown"),
                "currency": data.get("currencySymbol", "₹")
            }, None

    except Exception as e:
        logger.error(f"Scraper Error: {e}")
        return None, str(e)
