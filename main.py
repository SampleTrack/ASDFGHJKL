# main.py
import os
import asyncio
import logging
from pyrogram import Client
from aiohttp import web
from config import Telegram, Server
from helper.logger_setup import init_logger
from helper.price_checker import run_price_check

# --- config ---
PORT = int(os.environ.get("PORT", 7860))
HOST = "0.0.0.0"
CHECK_INTERVAL = 18000  # 5 hours

# --- logging ---
logger = logging.getLogger(__name__)
init_logger(None, __name__)  # adapt if your init_logger needs the client instance later

# --- pyrogram client ---
app = Client(
    Telegram.BOT_NICKNAME,
    api_id=Telegram.API_ID,
    api_hash=Telegram.API_HASH,
    bot_token=Telegram.BOT_TOKEN,
    plugins=dict(root="plugins"),
)

# --- aiohttp app (simple health endpoint) ---
async def handle_root(request):
    return web.Response(text="OK - Bot running")

async def start_http_server():
    aio_app = web.Application()
    aio_app.add_routes([web.get("/", handle_root)])
    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    logger.info("HTTP server started on %s:%s", HOST, PORT)
    return runner

async def stop_http_server(runner):
    if runner:
        await runner.cleanup()
        logger.info("HTTP server stopped")

# --- background periodic price checker ---
async def price_check_runner(client: Client):
    # run once immediately, then sleep between runs
    try:
        while True:
            try:
                logger.info("Price check: starting run")
                await run_price_check(client, manual_trigger=False)
                logger.info("Price check: completed run")
            except Exception:
                logger.exception("Error during price check run")
            await asyncio.sleep(CHECK_INTERVAL)
    except asyncio.CancelledError:
        logger.info("Price check runner cancelled, exiting")

# --- main lifecycle ---
async def main():
    http_runner = None
    price_task = None

    # Start HTTP server if configured to run server behavior
    if Server.IS_SERVER:
        http_runner = await start_http_server()

    # Start pyrogram client
    await app.start()
    logger.info("Pyrogram client started")

    # send restart message to admin (best effort)
    try:
        await app.send_message(Telegram.ADMIN, "Bot restarted")
    except Exception:
        logger.exception("Failed to send restart message to ADMIN")

    # schedule background price checker
    price_task = asyncio.create_task(price_check_runner(app))

    # keep the main loop alive until cancelled
    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("Main cancelled, shutting down")

    # shutdown sequence
    if price_task:
        price_task.cancel()
        try:
            await price_task
        except asyncio.CancelledError:
            pass

    if app.is_connected:
        await app.stop()
        logger.info("Pyrogram client stopped")

    if http_runner:
        await stop_http_server(http_runner)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted, exiting.")
    except Exception:
        logger.exception("Fatal error in main")
