from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
import os
import sys
import logging

# LOGGER import safe way
LOGGER = logging.getLogger(__name__)

# AUTH USERS
AUTH_USERS = [
    int(x) for x in str(Config.AUTH_USERS).split(",") if x.strip().isdigit()
]

# Prefixes (optional but plugins expect)
prefixes = ["/", "~", "?", "!"]

# Fallback for Pyrogram v2: filters.edited may not exist
if not hasattr(filters, "edited"):
    from pyrogram.filters import create as _create_filter

    def _is_edited(_, __, m):
        return getattr(m, "edit_date", None) is not None

    filters.edited = _create_filter(_is_edited)


# --------------------- START ---------------------
@Client.on_message(filters.command(["start"]) & ~filters.edited)
async def Start_msg(bot: Client, m: Message):
    await bot.send_photo(
        m.chat.id,
        photo="https://telegra.ph/file/cef3ef6ee69126c23bfe3.jpg",
        caption=(
            "**Hi i am All in One Extractor Bot**.\n"
            "Press **/pw** for Physics Wallah..\n\n"
            "Press **/e1** for E1 Coaching App..\n\n"
            "Press **/vidya** for Vidya Bihar App..\n\n"
            "Press **/ocean** for Ocean Gurukul App..\n\n"
            "Press **/winners** for The Winners Institute..\n\n"
            "Press **/rgvikramjeet** for Rgvikramjeet App..\n\n"
            "Press **/txt** for Ankit With Rojgar,\nThe Mission Institute,\nThe Last Exam App..\n\n"
            "Press **/cp** for Classplus App..\n\n"
            "Press **/cw** for Careerwill App..\n\n"
            "Press **/khan** for Khan GS App..\n\n"
            "Press **/exampur** for Exampur App..\n\n"
            "Press **/samyak** for Samyak IAS..\n\n"
            "Press **/chandra** for Chandra App..\n\n"
            "Press **/mgconcept** for MgConcept..\n\n"
            "Press **/down** for Downloading URL Lists..\n\n"
            "Press **/forward** to forward from one channel to others..\n\n"
            "**𝗕𝗼𝘁 𝗢𝘄𝗻𝗲𝗿 : @Btw_Salaar**"
        )
    )


# --------------------- RESTART ---------------------
@Client.on_message(filters.command(["restart"]) & filters.user(AUTH_USERS) & ~filters.edited)
async def restart_handler(bot: Client, m: Message):
    await m.reply_text("Restarting...", quote=True)
    os.execl(sys.executable, sys.executable, *sys.argv)


# --------------------- LOG ---------------------
@Client.on_message(filters.command(["log"]) & filters.user(AUTH_USERS) & ~filters.edited)
async def log_msg(bot: Client, m: Message):
    if os.path.exists("log.txt"):
        await bot.send_document(m.chat.id, "log.txt")
    else:
        await m.reply_text("Log file not found.", quote=True)
