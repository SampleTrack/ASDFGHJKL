import time
from pyrogram import Client as app, Client, filters
from pyrogram.types import Message
from helper.database import users, products
from config import Telegram
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@app.on_message(
    filters.command("stats") &
    filters.private &
    filters.user(Telegram.ADMIN)
)
async def get_stats(client: Client, message: Message):
    """
    Handles the /stats command for admins.
    Calculates and displays bot usage statistics based on active trackings.
    """
    start_time = time.time()
    stats_msg = await message.reply("⏳ **Calculating statistics, please wait...**", quote=True)

    try:
        # --- Database Queries ---
        all_users = list(users.find({}, {"user_id": 1, "trackings": 1}))
        total_users_count = len(all_users)

        # --- Data Processing ---

        # 1. Get a set of all unique product IDs currently tracked by any user.
        active_product_ids = {
            pid for user in all_users for pid in user.get("trackings", [])
        }

        # 2. Fetch only the active products to get their source.
        active_products_cursor = products.find(
            {"_id": {"$in": list(active_product_ids)}},
            {"_id": 1, "source": 1}
        )

        # 3. Dynamically tally all sources from the list of active products.
        source_counts = defaultdict(int)
        found_product_ids = set()
        for product in active_products_cursor:
            found_product_ids.add(product["_id"])
            source = product.get("source", "unknown")
            source_counts[source] += 1

        # 4. Recalculate user counts and total trackings based on found products.
        total_valid_trackings = 0
        user_tracking_counts = []
        for user in all_users:
            user_id = user.get("user_id")
            tracking_ids = user.get("trackings", [])

            if not user_id or not tracking_ids:
                continue

            # Count only trackings that point to an existing product.
            valid_count = sum(1 for pid in tracking_ids if pid in found_product_ids)

            if valid_count > 0:
                user_tracking_counts.append((user_id, valid_count))
            
            total_valid_trackings += valid_count

        # Sort users by tracking count to find the top 10
        top_10_users = sorted(user_tracking_counts, key=lambda item: item[1], reverse=True)[:10]

        # --- Format the Output ---
        
        # Dynamically create the list of sources and their counts
        source_stats_text = ""
        if source_counts:
            # Sort by source name for a consistent, alphabetical order
            for source, count in sorted(source_counts.items()):
                source_stats_text += f"  - **{source.capitalize()}:** `{count}` products\n"
        else:
            source_stats_text = "  No active products found.\n"
            
        top_users_text = ""
        if top_10_users:
            for i, (user_id, count) in enumerate(top_10_users):
                top_users_text += f"  `{i+1}.` User ID: `{user_id}` - **{count}** trackings\n"
        else:
            top_users_text = "  No users with active trackings found.\n"

        processing_time = time.time() - start_time

        # Final statistics message
        stats_text = (
            f"📊 **Bot Usage Statistics**\n\n"
            f"**👤 Total Users:** `{total_users_count}`\n"
            f"**🔗 Total Active Trackings:** `{total_valid_trackings}`\n\n"
            f"📈 **Trackings by Source (Active):**\n"
            f"{source_stats_text}\n"
            f"🏆 **Top 10 Users by Trackings:**\n"
            f"{top_users_text}\n\n"
            f"⏱️ `Report generated in {processing_time:.2f} seconds`"
        )

        await stats_msg.edit_text(stats_text)

    except Exception as e:
        logger.error(f"Error processing /stats for admin {message.from_user.id}: {e}", exc_info=True)
        await stats_msg.edit_text(f"❌ **An internal error occurred while generating stats.**\n_The error has been logged for review._")
