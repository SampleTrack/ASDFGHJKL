import aiohttp
import logging

logger = logging.getLogger(__name__)

async def fetch_product_info(url):
    """
    Fetches product details from the API.
    """
    api_url = "https://e-com-price-tracker-lemon.vercel.app/buyhatke"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, params={"product_url": url}, timeout=20) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                
                if "error" in data or "detail" in data:
                    return None
                
                return data
        except Exception as e:
            logger.error(f"API Fetch Error: {e}")
            return None
