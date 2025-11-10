#  MIT License (header as-is)

import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from config import Config
from pyrogram import Client, idle, filters

# ----- Optional: PyroMod enable (.ask & .listen for plugins)
try:
    from pyromod import listen  # noqa: F401
except Exception as e:
    logging.warning("PyroMod load warning: %s", e)

# -----------------------------------------
#               LOGGER
# -----------------------------------------
LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=5_000_000, backupCount=10),
        logging.StreamHandler(),
    ],
)

# -----------------------------------------
#       filters.edited FIX (plugins safe)
# -----------------------------------------
"""
Old plugins use:  @bot.on_message(filters.command(...) & ~filters.edited)

Pyrogram v2 removed filters.edited, so we patch it manually here.
"""
if not hasattr(filters, "edited"):
    from pyrogram.filters import create as _create_filter

    def _is_edited(_, __, m):
        return getattr(m, "edit_date", None) is not None

    filters.edited = _create_filter(_is_edited)

# -----------------------------------------
#         AUTH USERS LIST
# -----------------------------------------
AUTH_USERS = [int(x) for x in (Config.AUTH_USERS or "").split(",") if x.strip().isdigit()]

# -----------------------------------------
#           COMMAND PREFIXES
# -----------------------------------------
prefixes = ["/", "!", "?", "~"]

# -----------------------------------------
#        PLUGINS Directory Loader
# -----------------------------------------
plugins = dict(root="plugins")

# -----------------------------------------
#        HEALTH SERVER (Render)
# -----------------------------------------
async def _start_health_server():
    port = int(os.getenv("PORT", "0") or "0")

    if port <= 0:
        return

    try:
        from aiohttp import web

        async def ok(_):
            return web.Response(text="ok")

        app = web.Application()
        app.router.add_get("/", ok)

        runner = web.AppRunner(app)
        await runner.setup()

        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()

        LOGGER.info(f"Health server running at: 0.0.0.0:{port}")

    except Exception as e:
        LOGGER.warning("Health server failed: %s", e)

# -----------------------------------------
#             BOT INSTANCE
# -----------------------------------------
bot = Client(
    name="bot-session",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    sleep_threshold=20,
    plugins=plugins,
    workers=50,
)

# -----------------------------------------
#                 MAIN
# -----------------------------------------
async def main():

    # Health check for Render/Railway
    await _start_health_server()

    # Remove webhook safely (important for polling)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

    # Start bot
    await bot.start()
    me = await bot.get_me()
    LOGGER.info(f"<--- @{me.username} Started --->")

    # Small test command
    @bot.on_message(filters.command("ping"))
    async def _ping(_, m):
        await m.reply_text("pong ✅")

    await idle()

    await bot.stop()
    LOGGER.info("<--- Bot Stopped --->")


if __name__ == "__main__":
    asyncio.run(main())
