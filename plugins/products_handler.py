import re
import json
import httpx
import random
import string
import asyncio
import tempfile
import os
from pyrogram import Client as app, Client, filters
from pyrogram.types import (
    Message, InputMediaPhoto,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from pyrogram.errors import MediaCaptionTooLong
from helper.database import products, users
import logging

logger = logging.getLogger(__name__)

# This dictionary temporarily holds product data before it's saved to the database.
pending_tracks = {}

# --- Helper Functions ---

def generate_product_id(length=12):
    """Generates a random 12-character alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def parse_price(price_input):
    """
    Converts a price input (string, int, or float) into a dict 
    with string and integer values.
    """
    if isinstance(price_input, (int, float)):
        return {"string": str(price_input), "int": int(price_input)}
        
    if not isinstance(price_input, str):
        return {"string": "N/A", "int": 0}
    
    original_string = price_input.strip()
    cleaned_str = re.sub(r'[^\d.]', '', original_string)
    
    try:
        price_int = int(float(cleaned_str))
    except (ValueError, TypeError):
        price_int = 0
        
    return {"string": original_string, "int": price_int}

async def download_image(client: httpx.AsyncClient, url: str) -> str | None:
    """Downloads an image from a URL to a temporary file and returns the path."""
    try:
        response = await client.get(url, timeout=15)
        response.raise_for_status()
        
        suffix = ".jpg"
        if "webp" in url.lower() or response.headers.get("Content-Type", "").lower() == "image/webp":
            suffix = ".png"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
            
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        logger.warning(f"Could not download image {url}: {e}", exc_info=False)
        return None
    except Exception as e:
        logger.error(f"Unexpected error downloading image {url}: {e}", exc_info=True)
        return None

# --- Link and Tracking Button Handlers ---

# A broad regex to capture any valid URL. The API will handle unsupported domains.
URL_REGEX = r"https?://[^\s]+"

@app.on_message(filters.regex(URL_REGEX, re.IGNORECASE) & filters.private)
async def product_link_handler(client: Client, message: Message):
    """Handles incoming e-commerce links using the new centralized API endpoint."""
    product_url = message.matches[0].group(0)
    
    api_endpoint = "https://e-com-price-tracker-lemon.vercel.app/buyhatke"
    
    processing_msg = await message.reply("⏳ **Fetching product details, please wait...**", quote=True)
    
    downloaded_image_paths = []
    try:
        async with httpx.AsyncClient(timeout=45.0) as http_client:
            response = await http_client.get(api_endpoint, params={"product_url": product_url})
            
            # This will raise an exception for 4xx and 5xx responses, which is handled below
            response.raise_for_status()
            raw_data = response.json()

        # Handle cases where the API returns 200 OK but contains an error message
        if "error" in raw_data or "detail" in raw_data:
            error_detail = raw_data.get("error") or raw_data.get("detail")
            await processing_msg.edit(f"❌ **API Error:** {error_detail}")
            return

        # Extract the main product data and currency symbol
        product_main_data = raw_data.get("dealsData", {}).get("product_data")
        currency_symbol = raw_data.get("currencySymbol", "₹")

        if not product_main_data:
            await processing_msg.edit("❌ **Error:** Could not parse product details from the API response.")
            return

        product_id = generate_product_id()
        pending_tracks[product_id] = {
            "api_data": product_main_data,
            "url": product_url,
            "user_id": message.from_user.id,
            "source": product_main_data.get('site_name', 'unknown').lower(),
            "currency_symbol": currency_symbol
        }
        
        caption = (
            f"**{product_main_data.get('name', 'N/A')}**\n\n"
            f"**Price:** ~~{currency_symbol}{product_main_data.get('orgi_price', 'N/A')}~~ → **{currency_symbol}{product_main_data.get('cur_price', 'N/A')}** `({product_main_data.get('discount', 'N/A')}%)`\n"
            f"**Rating:** {product_main_data.get('rating', 'N/A')}⭐ ({product_main_data.get('ratingCount', 0)} ratings)"
        )

        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Start Tracking", callback_data=f"track_{product_id}")]])
        
        image_urls = product_main_data.get("thumbnailImages", [])
        
        if image_urls:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                tasks = [download_image(http_client, url) for url in image_urls[:10]]
                results = await asyncio.gather(*tasks)
                downloaded_image_paths = [path for path in results if path]

        if not downloaded_image_paths:
            await processing_msg.edit(caption, reply_markup=keyboard)
            return

        media_to_send = [InputMediaPhoto(media=downloaded_image_paths[0], caption=caption)]
        media_to_send.extend([InputMediaPhoto(media=path) for path in downloaded_image_paths[1:]])
            
        await client.send_media_group(chat_id=message.chat.id, media=media_to_send, reply_to_message_id=message.id)
        await client.send_message(
            chat_id=message.chat.id,
            text="Press the button below to start tracking this item.",
            reply_markup=keyboard,
            reply_to_message_id=message.id
        )
        await processing_msg.delete()

    except MediaCaptionTooLong:
        await processing_msg.edit("❌ **Error:** The product title is too long to be sent as a caption.")
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTPStatusError for {product_url}: Status {e.response.status_code}", exc_info=True)
        # ✅ **FIX:** Smartly handle HTTP errors by checking the response body first.
        try:
            error_data = e.response.json()
            error_detail = error_data.get("error") or error_data.get("detail", "")
            
            if "PID not found in URL, even after attempting to expand" in error_detail:
                await processing_msg.edit(
                    "❌ **Failed to retrieve data.**\n\n"
                    "This might be because you sent a shortened product link. "
                    "Please open the shortlink in your browser and paste the full, redirected URL."
                )
            else:
                await processing_msg.edit(f"❌ **API Error:** {error_detail}")
        except (json.JSONDecodeError, AttributeError):
            # Fallback for non-JSON errors or unexpected structures
            await processing_msg.edit(f"❌ **Error:** The API service responded with an error: `Status {e.response.status_code}`")

    except httpx.RequestError as e:
        logger.error(f"RequestError for {product_url}: {e}", exc_info=True)
        await processing_msg.edit("❌ **Error:** Could not connect to the price tracker service.")
    except Exception as e:
        logger.error(f"Unexpected error for {product_url}: {e}", exc_info=True)
        await processing_msg.edit("❌ **An unexpected error occurred.**")
    finally:
        for path in downloaded_image_paths:
            try:
                os.remove(path)
            except OSError as e:
                logger.error(f"Error removing temp file {path}: {e}")

@app.on_callback_query(filters.regex(r"^track_"))
async def track_button_handler(client: Client, callback_query: CallbackQuery):
    """Handles the 'Start Tracking' button click and saves data to the database."""
    product_id = callback_query.data.split("_", 1)[1]
    user_id = callback_query.from_user.id

    product_data = pending_tracks.get(product_id)
    if not product_data or product_data.get("user_id") != user_id:
        await callback_query.answer("This request has expired. Please send the link again.", show_alert=True)
        return

    try:
        api_data = product_data["api_data"]
        
        product_doc = {
            '_id': product_id,
            'userid': user_id,
            'url': product_data["url"],
            'source': product_data["source"],
            'currency': product_data.get("currency_symbol", "₹"),
            'product_name': api_data.get('name'),
            'current_price': parse_price(api_data.get('cur_price')),
            'original_price': parse_price(api_data.get('orgi_price')),
            'discount_percentage': api_data.get('discount'),
            'rating': api_data.get('rating'),
            'reviews_count': api_data.get('ratingCount'),
            'images': api_data.get('thumbnailImages', []),
            'other_details': {
                'brand': api_data.get('brand'),
                'category': api_data.get('category'),
                'pid': api_data.get('pid')
            }
        }
        
        products.insert_one(product_doc)
        users.update_one(
            {"user_id": str(user_id)},
            {"$push": {"trackings": product_id}},
            upsert=True
        )
        del pending_tracks[product_id]

        await callback_query.answer("✅ Successfully started tracking this product!", show_alert=True)
        await callback_query.message.edit_text(
            text="**✅ Successfully started tracking this product!**\nSend /my_trackings to see all your tracked items."
        )
        
    except Exception as e:
        logger.error(f"DB error for user {user_id}, product {product_id}: {e}", exc_info=True)
        await callback_query.answer("A database error occurred. Please try again.", show_alert=True)
