import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from pyrogram import Client, idle, filters

try:
    from pyromod import listen
except:
    pass

# Logging
LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(message)s",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=5_000_000, backupCount=5),
        logging.StreamHandler(),
    ],
)

# filters.edited fix (old plugins dependent)
if not hasattr(filters, "edited"):
    from pyrogram.filters import create
    def _is_edited(_, __, m): return getattr(m, "edit_date", None) is not None
    filters.edited = create(_is_edited)

# ENV CONFIG
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
AUTH_USERS = [int(x) for x in os.getenv("AUTH_USERS", "").split(",") if x.strip().isdigit()]

plugins = dict(root="plugins")

# Render health port
async def health_server():
    port = int(os.getenv("PORT", "0") or 0)
    if port == 0:
        return
    try:
        from aiohttp import web
        async def ok(_):
            return web.Response(text="ok")
        app = web.Application()
        app.router.add_get("/", ok)
        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", port).start()
        LOGGER.info(f"Health server running on {port}")
    except Exception as e:
        LOGGER.warning(f"Health server error: {e}")

bot = Client(
    "bot-session",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    plugins=plugins,
    workers=50,
    sleep_threshold=20,
)

async def main():
    await health_server()
    await bot.start()
    me = await bot.get_me()
    LOGGER.info(f"<--- @{me.username} Started --->")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
