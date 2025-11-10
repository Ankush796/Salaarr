#  MIT License (header as-is)

import os
import sys
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from pyrogram import Client, idle, filters
from config import Config

# ---------- Make this module importable as "main" for plugins ----------
# (Many plugins do: from main import LOGGER, prefixes, AUTH_USERS)
sys.modules.setdefault("main", sys.modules[__name__])

# ---------- Optional: PyroMod enable (.ask/.listen used by plugins) ----------
try:
    from pyromod import listen  # noqa: F401
except Exception as e:
    logging.warning("PyroMod load warning: %s", e)

# ---------- Logger ----------
LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=5_000_000, backupCount=10),
        logging.StreamHandler(),
    ],
)

# ---------- filters.edited shim (Pyrogram v2 compatibility for old plugins) ----------
if not hasattr(filters, "edited"):
    from pyrogram.filters import create as _create_filter  # type: ignore

    def _is_edited(_, __, m):
        return getattr(m, "edit_date", None) is not None

    filters.edited = _create_filter(_is_edited)

# ---------- Auth users & command prefixes (plugins import these) ----------
AUTH_USERS = [int(x) for x in (Config.AUTH_USERS or "").split(",") if x.strip().isdigit()]
prefixes = ["/", "!", "?", "~"]

# ---------- Pyrogram plugins loader (points to ./plugins package) ----------
plugins = dict(root="plugins")

# ---------- Tiny health server (Render/Railway) ----------
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
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    sleep_threshold=20,
    plugins=plugins,   # <-- auto-load modules from ./plugins
    workers=50,
)

async def main():
    # Health endpoint
    await _start_health_server()

    # Safety: clear webhook (polling mode)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass

    # Start
    await bot.start()
    me = await bot.get_me()
    LOGGER.info("<--- @%s Started --->", me.username)

    # Minimal sanity cmd (in case plugins fail)
    @bot.on_message(filters.command("ping"))
    async def _ping(_, m):
        await m.reply_text("pong ✅")

    await idle()

    await
