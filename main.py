#  MIT License header as-is

import os
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from config import Config
from pyrogram import Client, idle, filters

# --- Optional: PyroMod (just importing enables conversations) ---
try:
    from pyromod import listen  # noqa
except Exception as e:
    logging.warning("PyroMod load warning: %s", e)

# ---------- Logger (exported) ----------
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

# ---------- filters.edited shim (so ~filters.edited works) ----------
if not hasattr(filters, "edited"):
    from pyrogram.filters import create as _create_filter  # type: ignore

    def _is_edited(_, __, m):
        return getattr(m, "edit_date", None) is not None

    filters.edited = _create_filter(_is_edited)

# ---------- Auth Users (exported) ----------
AUTH_USERS = [int(x) for x in (Config.AUTH_USERS or "").split(",") if x.strip().isdigit()]

# ---------- Prefixes (exported, plugins import this) ----------
prefixes = ["/", "~", "?", "!"]

# ---------- Plugins root ----------
plugins = dict(root="plugins")

# ---------- Tiny HTTP server for Render (binds $PORT) ----------
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
        LOGGER.info("Health server running on 0.0.0.0:%s", port)
    except Exception as e:
        LOGGER.warning("Health server failed: %s", e)

# ---------- Bot client ----------
bot = Client(
    name="bot-session",
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    sleep_threshold=20,
    plugins=plugins,
    workers=50,
)

async def main():
    await _start_health_server()
    await bot.start()
    me = await bot.get_me()
    LOGGER.info(f"<--- @{me.username} Started --->")
    await idle()
    await bot.stop()
    LOGGER.info("<--- Bot Stopped --->")

if __name__ == "__main__":
    asyncio.run(main())
