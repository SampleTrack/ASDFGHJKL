import asyncio
import re
import httpx
import os
import logging
from datetime import datetime
from collections import defaultdict

from pyrogram import Client
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions
)
from pyrogram.errors import (
    UserIsBlocked,
    PeerIdInvalid,
    MessageNotModified
)

from config import Telegram
from helper.database import products, users

# --- Configuration & Setup ---
logger = logging.getLogger(__name__)

preview_options = LinkPreviewOptions(
    show_above_text=True,
    prefer_small_media=True
)

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, "price_check.log")


# --- Helper Functions ---

def parse_price_obj(price_input) -> dict:
    """
    Converts a price (str, int, float) into a standard dictionary
    {"string": "...", "int": ...} for the database.
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


def format_duration(seconds: float) -> str:
    """Formats a duration in seconds into a human-readable string (hh:mm:ss)."""
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    elif minutes > 0:
        return f"{minutes:02}:{seconds:02}"
    else:
        return f"{seconds}s"


async def fetch_product_data(client: httpx.AsyncClient, product_doc: dict, log_file):
    """Fetches and processes data for a single product using the new API structure."""
    product_id = product_doc["_id"]
    product_url = product_doc.get("url")
    log_file.write(f"\n🔍 Checking: {product_url}\n")

    if not product_url:
        log_file.write("❌ Error: Missing URL\n")
        return product_id, {"error": "Missing URL"}

    api_url = f"https://e-com-price-tracker-lemon.vercel.app/buyhatke?product_url={product_url}"

    try:
        response = await client.get(api_url)
        response.raise_for_status()
        api_data = response.json()

        if "error" in api_data or "detail" in api_data:
            error_msg = api_data.get("error") or api_data.get("detail")
            log_file.write(f"❌ API Error: {error_msg}\n")
            return product_id, {"error": error_msg, "status": "error"}

    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as e:
        log_file.write(f"❌ Network/JSON Error: {e}\n")
        return product_id, {"error": str(e), "status": "error"}

    # Data Normalization
    product_main_data = api_data.get("dealsData", {}).get("product_data")
    currency_symbol = api_data.get("currencySymbol", "₹")

    if not product_main_data:
        log_file.write("❌ Error: 'product_data' not found in API response\n")
        return product_id, {"error": "'product_data' not found", "status": "error"}

    new_price_int = parse_price_obj(product_main_data.get("cur_price")).get("int", 0)
    old_price_int = product_doc.get("current_price", {}).get("int", 0)

    # Compare prices and prepare updates
    result = {"status": "same"}
    if new_price_int == 0 or new_price_int == old_price_int:
        log_file.write("✅ Price Change: Nil\n")
        return product_id, result

    price_change_percent = ((new_price_int - old_price_int) / old_price_int) * 100 if old_price_int > 0 else 0

    update_payload = {
        "product_name": product_main_data.get("name", product_doc.get("product_name")),
        "currency": currency_symbol,
        "current_price": parse_price_obj(product_main_data.get("cur_price")),
        "original_price": parse_price_obj(product_main_data.get("orgi_price")),
        "discount_percentage": product_main_data.get("discount"),
        "rating": product_main_data.get("rating"),
        "reviews_count": product_main_data.get("ratingCount"),
        "images": product_main_data.get("thumbnailImages", []),
    }
    result["update_payload"] = update_payload

    # Prepare notification text
    product_name = product_main_data.get("name", "N/A")
    old_price_str = product_doc.get("current_price", {}).get("string", "N/A")
    new_price_str = update_payload["current_price"]["string"]
    image_url = (update_payload["images"][0] if update_payload.get("images") else None)
    button = InlineKeyboardMarkup([[InlineKeyboardButton("Buy Now 🛍️", url=product_url)]])

    if new_price_int > old_price_int:
        log_file.write(f"📈 Price Change: Increased by +{price_change_percent:.2f}%\n")
        result["status"] = "increased"
        result["notification_text"] = (
            f"🔺 **Price Increased!**\n\n"
            f"**Product:** [{product_name}]({product_url})\n"
            f"**Old Price:** `{currency_symbol}{old_price_str}`\n"
            f"**New Price:** `{currency_symbol}{new_price_str}`\n"
            f"**Change:** `+{price_change_percent:.2f}%`"
        )
    else:
        log_file.write(f"📉 Price Change: Decreased by {price_change_percent:.2f}%\n")
        result["status"] = "decreased"
        result["notification_text"] = (
            f"✅ **Price Dropped!**\n\n"
            f"**Product:** [{product_name}]({product_url})\n"
            f"**Old Price:** `{currency_symbol}{old_price_str}`\n"
            f"**New Price:** `{currency_symbol}{new_price_str}`\n"
            f"**Change:** `{price_change_percent:.2f}%`"
        )

    result["notification_text"] += f"\n\n[\u200b]({image_url})" if image_url else ""
    result["button"] = button

    return product_id, result


async def save_and_send_logs(client: Client, summary_text: str, log_file_path: str):
    """Sends the summary, then the log file if it's not empty, and finally deletes it."""
    try:
        await client.send_message(
            chat_id=Telegram.LOG_CHANNEL_ID,
            reply_to_message_id=Telegram.CHECKER_LOG_TOPIC,
            text=summary_text,
        )
    except Exception as e:
        logger.error(f"Failed to send summary to log channel: {e}", exc_info=True)

    try:
        if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 0:
            await client.send_document(
                chat_id=Telegram.LOG_CHANNEL_ID,
                document=log_file_path,
                caption=f"📋 Price Check Logs for {datetime.now().strftime('%Y-%m-%d')}",
                reply_to_message_id=Telegram.CHECKER_LOG_TOPIC,
            )
        else:
            print(f"INFO: Log file '{log_file_path}' not sent because it is missing or empty.")
    except Exception as e:
        logger.error(f"Failed to send or process log file: {e}", exc_info=True)
    finally:
        if os.path.exists(log_file_path):
            os.remove(log_file_path)


async def run_price_check(client: Client, manual_trigger: bool = False, status_msg: Message = None):
    """Checks product prices, cleans up dead links, and notifies users."""
    start_time = datetime.now()
    summary_text = "🤷‍♂️ No products are currently being tracked."

    if manual_trigger and status_msg:
        try:
            await status_msg.edit_text("🔎 **Initializing Price Check...**")
        except MessageNotModified:
            pass

    with open(LOG_FILE_PATH, "w") as log_file:
        log_file.write(f"*** Price Check Run Log: {start_time.strftime('%Y-%m-%d %H:%M:%S')} ***\n")

        # --- Step 1: Data Aggregation, Validation, and Cleanup ---
        product_to_users_map = defaultdict(list)
        valid_product_ids = set()
        missing_refs_count = 0
        users_to_notify_for_cleanup = set()
        
        all_users = list(users.find({}, {"user_id": 1, "trackings": 1}))
        users_with_trackings = {doc['user_id'] for doc in all_users if doc.get("trackings")}
        total_active_trackings = 0

        log_file.write("\n--- Database Cleanup Phase ---\n")
        for user_doc in all_users:
            user_id = user_doc.get("user_id")
            tracking_ids = user_doc.get("trackings", [])
            if not user_id or not tracking_ids:
                continue

            total_active_trackings += len(tracking_ids)
            valid_ids_for_user = []
            missing_ids_for_user = []

            for product_id in tracking_ids:
                if products.count_documents({"_id": product_id}) > 0:
                    valid_ids_for_user.append(product_id)
                    product_to_users_map[product_id].append(user_id) # ✅ FIX: Changed .add to .append
                else:
                    missing_ids_for_user.append(product_id)
                    log_file.write(f"Found missing ref '{product_id}' for user '{user_id}'\n")

            valid_product_ids.update(valid_ids_for_user)

            if missing_ids_for_user:
                missing_refs_count += len(missing_ids_for_user)
                users.update_one(
                    {"user_id": user_id},
                    {"$pull": {"trackings": {"$in": missing_ids_for_user}}}
                )
                users_to_notify_for_cleanup.add(user_id)
                log_file.write(f"Removed {len(missing_ids_for_user)} refs for user '{user_id}'\n")
        
        # --- Step 2: Notify Users About Cleanup ---
        if users_to_notify_for_cleanup:
            cleanup_tasks = []
            notification_text = (
                "Sorry, one of your tracked items was removed because it was no longer valid in our database.\n\n"
                "Please use /my_trackings to verify your current list."
            )
            for user_id in users_to_notify_for_cleanup:
                cleanup_tasks.append(client.send_message(chat_id=int(user_id), text=notification_text))
            
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
            log_file.write(f"\nSent cleanup notifications to {len(users_to_notify_for_cleanup)} users.\n")


        if not valid_product_ids:
            log_file.write("\nNo valid products found to check.\n")
            if manual_trigger and status_msg:
                await status_msg.edit_text(summary_text)
        else:
            # --- Step 3: Fetch and Process Valid Products ---
            product_docs = {doc["_id"]: doc for doc in products.find({"_id": {"$in": list(valid_product_ids)}})}
            log_file.write(f"\n--- Price Check Phase ({len(product_docs)} products) ---\n")
            
            if manual_trigger and status_msg:
                await status_msg.edit_text(f"⚙️ **Checking {len(product_docs)} products...**")

            results = []
            async with httpx.AsyncClient(timeout=45.0) as http_client:
                for i, doc in enumerate(product_docs.values()):
                    await asyncio.sleep(3)
                    product_id, result = await fetch_product_data(http_client, doc, log_file)
                    results.append((product_id, result))
                    if manual_trigger and status_msg and (i + 1) % 10 == 0:
                        await status_msg.edit_text(f"⚙️ **Checking products... `({i + 1}/{len(product_docs)})`**")

            # --- Step 4: Process Results and Send Price Notifications ---
            counters = defaultdict(int)
            platform_stats = defaultdict(lambda: defaultdict(int))
            notification_tasks = []
            unique_users_to_notify = set()

            for product_id, result in results:
                counters["checked"] += 1
                status = result.get("status", "error")
                counters[status] += 1
                source = product_docs.get(product_id, {}).get("source", "unknown").lower()
                platform_stats[source]["checked"] += 1
                platform_stats[source][status] += 1

                if "update_payload" in result:
                    products.update_one({"_id": product_id}, {"$set": result["update_payload"]})

                if "notification_text" in result:
                    for user_id in product_to_users_map.get(product_id, []):
                        unique_users_to_notify.add(user_id)
                        platform_stats[source]["notified"] += 1
                        notification_tasks.append(
                            client.send_message(
                                chat_id=int(user_id),
                                text=result["notification_text"],
                                reply_markup=result.get("button"),
                                link_preview_options=preview_options
                            )
                        )
            
            sent_results = await asyncio.gather(*notification_tasks, return_exceptions=True)
            notifications_sent = sum(1 for r in sent_results if not isinstance(r, Exception))
            notifications_failed = len(sent_results) - notifications_sent

            # --- Step 5: Generate Final Summary ---
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            time_taken_str = format_duration(total_duration)
            date_header = start_time.strftime("#%b%d")
            checked_count = counters['checked']
            avg_time_per_product = f"{total_duration / checked_count:.2f}s" if checked_count > 0 else "N/A"

            platform_summary_lines = []
            for platform, stats in sorted(platform_stats.items()):
                if stats["checked"] == 0: continue
                platform_summary_lines.append(f"🌐 **{platform.capitalize()}**: `{stats['checked']}` checked, `{stats['decreased']}` drops, `{stats['error']}` errors.")
            platform_summary_text = "\n".join(platform_summary_lines) if platform_summary_lines else "⚠️ No platform data."

            notif_summary = (
                f"**🔔 Price Notifications:**\n"
                f"- Unique Users Notified: `{len(unique_users_to_notify)}`\n"
                f"- Total Sent: `{notifications_sent}/{len(notification_tasks)}` | Failed: `{notifications_failed}`"
            )

            summary_text = (
                f"**{date_header} Price Check Complete!**\n\n"
                f"📊 **Overall Summary:**\n"
                f"- Products Checked: `{checked_count}`\n"
                f"- Active Trackings: `{total_active_trackings}`\n"
                f"- Users with Trackings: `{len(users_with_trackings)}`\n\n"
                f"📈 **Price Changes:**\n"
                f"- Increased: `{counters['increased']}` | Decreased: `{counters['decreased']}`\n\n"
                f"🔍 **Per-Platform:**\n{platform_summary_text}\n\n"
                f"{notif_summary}\n\n"
                f"⚙️ **System Health:**\n"
                f"- API/Scraping Errors: `{counters['error']}`\n"
                f"- Cleaned Product Refs: `{missing_refs_count}`\n\n"
                f"⏱️ **Performance:**\n"
                f"- Avg. Time per Product: `{avg_time_per_product}`\n"
                f"- Total Time Taken: `{time_taken_str}`"
            )

            if manual_trigger and status_msg:
                try:
                    await status_msg.edit_text(summary_text)
                except MessageNotModified: pass
                except Exception as e:
                    logger.error(f"Failed to edit status message: {e}", exc_info=True)

    await save_and_send_logs(client, summary_text, LOG_FILE_PATH)
