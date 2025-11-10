#  MIT License
#  Code edited By Cryptostark (Cleaned & Fixed Version)

import time
import os
import json
import requests
import cloudscraper
from pyromod import listen
from pyrogram import Client as bot, filters
from pyrogram.types import Message

# MAIN IMPORTS FOR LOGGER / PREFIXES / AUTH
from main import LOGGER, prefixes, AUTH_USERS
from config import Config


# ------------------------------
# ✅ FORWARD COMMAND (FIXED)
# ------------------------------
@bot.on_message(
    filters.private &
    filters.chat(AUTH_USERS) &
    filters.command("forward", prefixes=prefixes)
)
async def forward_handler(bot: bot, m: Message):

    # STEP 1 – GET TARGET CHANNEL
    msg = await bot.ask(
        m.chat.id,
        "**Forward ANY one message from the TARGET channel\n\n⚠️ Bot must be admin in BOTH channels**"
    )
    t_chat = msg.forward_from_chat.id

    # STEP 2 – START MESSAGE
    msg1 = await bot.ask(
        m.chat.id,
        "**Send the FIRST message from where forwarding should START**"
    )

    # STEP 3 – END MESSAGE
    msg2 = await bot.ask(
        m.chat.id,
        "**Send the LAST message from where forwarding should END**"
    )

    i_chat = msg1.forward_from_chat.id
    s_msg = int(msg1.forward_from_message_id)
    f_msg = int(msg2.forward_from_message_id) + 1

    await m.reply_text(
        "**✅ Forwarding Started**\n\nUse /restart to stop and /log to download logs."
    )

    try:
        for msg_id in range(s_msg, f_msg):
            try:
                await bot.copy_message(
                    chat_id=t_chat,
                    from_chat_id=i_chat,
                    message_id=msg_id
                )
            except Exception:
                continue
    except Exception as e:
        await m.reply_text(f"❌ Error: `{str(e)}`")

    await m.reply_text("✅ Done Forwarding ✅")
