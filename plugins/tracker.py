import random
import string
import io
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, LinkPreviewOptions
from config import Config
from helper.database import db
from helper.utils import fetch_product_info
from Script import Script

# Set Matplotlib to Headless mode (server safe)
matplotlib.use('Agg')

PENDING_TRACKS = {}
url_pattern = r"https?://[^\s]+"
NO_IMAGE_URL = "https://t4.ftcdn.net/jpg/04/70/29/97/360_F_470299797_UD0eoVMMSUbHCcNJCdv2t8B2g1GVqYgs.jpg"

@Client.on_message(filters.regex(url_pattern) & filters.private)
async def process_link(client, message):
    user_id = message.from_user.id
    if await db.is_banned(user_id): return
    
    lang = await db.get_lang(user_id)
    strs = Script.STRINGS[lang]

    url = message.matches[0].group(0)
    status = await message.reply(strs['fetching'], quote=True)

    data = await fetch_product_info(url)
    if not data or not data.get('dealsData'):
        return await status.edit("❌ **Error:** Could not fetch details.")

    product_data = data['dealsData']['product_data']
    currency = data.get('currencySymbol', '₹')
    
    cur_price_str = str(product_data.get('cur_price', '0'))
    try: cur_price_int = int(float(cur_price_str.replace(',', '').replace(currency, '').strip()))
    except: cur_price_int = 0
        
    org_price_str = str(product_data.get('orgi_price', cur_price_str))
    try: org_price_int = int(float(org_price_str.replace(',', '').replace(currency, '').strip()))
    except: org_price_int = 0

    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    real_product_id = str(product_data.get('pid', '')) or ''.join(random.choices(string.ascii_letters, k=12))

    thumbnails = product_data.get('thumbnailImages', [])
    image_url = thumbnails[0] if thumbnails else NO_IMAGE_URL

    temp_data = {
        "_id": real_product_id,
        "product_name": product_data.get('name', 'Unknown'),
        "url": url,
        "current_price": {"string": cur_price_str, "int": cur_price_int},
        "original_price": {"string": org_price_str, "int": org_price_int},
        "currency": currency,
        "image": image_url,
        "source": product_data.get('site_name', 'Unknown')
    }
    PENDING_TRACKS[session_id] = temp_data

    text = f"**🛒 Preview**\n**Name:** {temp_data['product_name'][:50]}...\n**Price:** {currency}{cur_price_str}\n\n__Start tracking?__"
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Start Tracking", callback_data=f"track_{session_id}"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel_track")]
    ])
    
    try: 
        await message.reply_photo(photo=temp_data['image'], caption=text, reply_markup=buttons, quote=True)
        await status.delete()
    except: 
        await status.edit(text, reply_markup=buttons)

@Client.on_callback_query(filters.regex(r"^track_"))
async def start_tracking_handler(client, callback: CallbackQuery):
    session_id = callback.data.split("_")[1]
    user_id = callback.from_user.id
    product_data = PENDING_TRACKS.get(session_id)
    
    lang = await db.get_lang(user_id)
    strs = Script.STRINGS[lang]

    if not product_data:
        return await callback.answer("⚠️ Session expired.", show_alert=True)

    try:
        try: await db.add_product(product_data)
        except: pass

        current_price = product_data['current_price']['int']
        await db.add_tracking_to_user(user_id, product_data['_id'], current_price)
        
        del PENDING_TRACKS[session_id]

        new_text = strs['tracking_started'].format(price=f"{product_data['currency']}{product_data['current_price']['string']}")
        btn = InlineKeyboardMarkup([[InlineKeyboardButton(strs['view_details_btn'], callback_data=f"view_{product_data['_id']}")]])
        await callback.message.edit_caption(caption=new_text, reply_markup=btn)

    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)

@Client.on_callback_query(filters.regex("cancel_track"))
async def cancel_handler(client, callback):
    await callback.message.delete()

# --- List Trackings ---
async def get_tracking_list_content(user_id, is_callback=False):
    user = await db.get_user(user_id)
    lang = user.get("lang", "en") if user else "en"
    strs = Script.STRINGS[lang]
    
    if not user or not user.get("trackings"):
        btn = [[InlineKeyboardButton(strs['back_btn'], callback_data="home_page")]] if is_callback else None
        return strs['empty_list'], btn
    
    track_list = user['trackings']
    buttons = []
    
    for item in track_list:
        tid = item['id'] if isinstance(item, dict) else item
        prod = await db.get_product(tid)
        if prod:
            buttons.append([InlineKeyboardButton(f"📦 {prod['product_name'][:30]}...", callback_data=f"view_{tid}")])
    
    if is_callback:
        buttons.append([InlineKeyboardButton(strs['back_btn'], callback_data="home_page"), InlineKeyboardButton("❌ Close", callback_data="close_menu")])
    return strs['tracking_list'], buttons

@Client.on_message(filters.command("trackings") & filters.private)
async def trackings_command(client, message):
    text, buttons = await get_tracking_list_content(message.from_user.id)
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None, quote=True)

@Client.on_callback_query(filters.regex("my_trackings"))
async def my_trackings_cb(client, callback):
    text, buttons = await get_tracking_list_content(callback.from_user.id, is_callback=True)
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# --- View Product & Graph ---
@Client.on_callback_query(filters.regex(r"^view_"))
async def view_product(client, callback):
    prod_id = callback.data.split("_")[1]
    prod = await db.get_product(prod_id)
    user = await db.get_user(callback.from_user.id)
    
    if not prod:
        await callback.answer("❌ Product not found.", show_alert=True)
        return await my_trackings_cb(client, callback)

    lang = user.get("lang", "en")
    strs = Script.STRINGS[lang]

    currency = prod.get('currency', '₹')
    curr_price = prod['current_price']['int']
    curr_price_str = prod['current_price']['string']
    
    added_price = 0
    for item in user.get('trackings', []):
        if isinstance(item, dict) and item['id'] == prod_id:
            added_price = item.get('added_price', 0)
            break
            
    if added_price > 0:
        if curr_price < added_price:
            diff = added_price - curr_price
            percent = int((diff / added_price) * 100)
            added_txt = strs['dropped'].format(currency=currency, diff=diff, percent=percent)
        elif curr_price > added_price:
            diff = curr_price - added_price
            percent = int((diff / added_price) * 100)
            added_txt = strs['increased'].format(currency=currency, diff=diff, percent=percent)
        else:
            added_txt = strs['no_change']
    else:
        added_txt = "⚠️ History N/A"

    img_link = f"[\u200b]({prod['image']})" if prod.get('image') else ""
    text = (f"{img_link}**📦 {prod['product_name']}**\n\n"
            f"🏪 **Source:** {prod['source']}\n"
            f"💰 **Current:** {currency}{curr_price_str}\n\n{added_txt}")

    buttons = [
        [InlineKeyboardButton(strs['buy_btn'], url=prod['url']), InlineKeyboardButton(strs['graph_btn'], callback_data=f"graph_{prod_id}")],
        [InlineKeyboardButton(strs['remove_btn'], callback_data=f"del_{prod_id}")],
        [InlineKeyboardButton(strs['back_btn'], callback_data="my_trackings")]
    ]

    try: await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    except: await callback.message.edit_text(text.replace("\u200b", ""), reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^graph_"))
async def graph_handler(client, callback):
    prod_id = callback.data.split("_")[1]
    prod = await db.get_product(prod_id)
    user_id = callback.from_user.id
    lang = await db.get_lang(user_id)
    strs = Script.STRINGS[lang]

    history = prod.get('price_history', [])
    
    if not history or len(history) < 1:
        return await callback.answer(strs['no_history'], show_alert=True)

    await callback.answer("🎨 Generating Graph...", show_alert=False)

    dates = [entry['date'] for entry in history]
    prices = [entry['price'] for entry in history]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, prices, marker='o', linestyle='-', color='b')
    plt.title(f"Price History: {prod['product_name'][:20]}...")
    plt.xlabel('Date')
    plt.ylabel(f"Price ({prod.get('currency', '₹')})")
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gcf().autofmt_xdate()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    await callback.message.reply_photo(
        photo=buf,
        caption=strs['graph_caption'].format(name=prod['product_name'][:30]),
        quote=True
    )
    buf.close()

@Client.on_callback_query(filters.regex(r"^del_"))
async def delete_product(client, callback):
    prod_id = callback.data.split("_")[1]
    await db.delete_product_tracking(callback.from_user.id, prod_id)
    lang = await db.get_lang(callback.from_user.id)
    await callback.answer(Script.STRINGS[lang]['removed'], show_alert=False)
    await my_trackings_cb(client, callback)
