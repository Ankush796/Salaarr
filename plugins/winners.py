#  MIT License
#
#  Copyright ...
#  Code edited By Cryptostark

import urllib
import urllib.parse
import requests
import json
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait
import time
from p_bar import progress_bar
from subprocess import getstatusoutput
import logging
import os
import sys
import re
from pyrogram import Client as bot
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

@bot.on_message(filters.command(["winners"]))
async def account_login(bot: Client, m: Message):
    global cancel
    cancel = False

    editable = await m.reply_text(
        "Send **ID & Password** in this manner otherwise bot will not respond.\n\nSend like this:-  **ID*Password**"
    )

    rwa_url = "https://winnersinstituteapi.classx.co.in/post/userLogin"
    hdr = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Authorization": "",
        "User_app_category": "",
        "Language": "en",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "233",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "okhttp/4.9.1"
    }

    info = {"email": "", "password": ""}

    input1: Message = await bot.listen(editable.chat.id)
    raw_text = input1.text
    info["email"] = raw_text.split("*")[0]
    info["password"] = raw_text.split("*")[1]
    await input1.delete(True)

    scraper = cloudscraper.create_scraper()
    res = scraper.post(rwa_url, data=info, headers=hdr).content
    output = json.loads(res)

    userid = output["data"]["userid"]
    token = output["data"]["token"]

    hdr1 = {
        "Host": "winnersinstituteapi.classx.co.in",
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": userid,
        "Authorization": token
    }

    await editable.edit("**login Successful**")

    res1 = requests.get(
        f"https://winnersinstituteapi.classx.co.in/get/mycourse?userid={userid}",
        headers=hdr1
    )

    b_data = res1.json()['data']
    cool = ""
    FFF = "**BATCH-ID - BATCH NAME - INSTRUCTOR**"

    for data in b_data:
        aa = f" ```{data['id']}```      - **{data['course_name']}**\n\n"
        if len(f"{cool}{aa}") > 4096:
            cool = ""
        cool += aa

    await editable.edit(f"**You have these batches :-**\n\n{FFF}\n\n{cool}")

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input2 = await bot.listen(editable.chat.id)
    raw_text2 = input2.text

    html = scraper.get(
        f"https://winnersinstituteapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={raw_text2}",
        headers=hdr1
    ).content

    subjID = json.loads(html)["data"]
    await m.reply_text(subjID)

    editable1 = await m.reply_text("**Enter the Subject Id shown above**")
    input3 = await bot.listen(editable.chat.id)
    raw_text3 = input3.text

    res3 = requests.get(
        f"https://winnersinstituteapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={raw_text2}&subjectid={raw_text3}",
        headers=hdr1
    )

    b_data2 = res3.json()['data']

    vj = ""
    cool1 = ""
    BBB = "**TOPIC-ID    - TOPIC     - VIDEOS**\n"

    for data in b_data2:
        tid = data["topicid"]
        tname = data["topic_name"]
        vj += f"{tid}&"

        hh = f"```{tid}```     - **{tname}**\n"
        if len(f"{cool1}{hh}") > 4096:
            cool1 = ""
        cool1 += hh

    await m.reply_text(f"Batch details:\n\n{BBB}\n{cool1}")

    editable = await m.reply_text(
        f"Now send the **Topic IDs** to Download\n\n"
        f"Send like: **1&2&3** etc.\n\n"
        f"**Full batch:**\n```{vj}```"
    )

    input4 = await bot.listen(editable.chat.id)
    raw_text4 = input4.text

    editable3 = await m.reply_text("**Now send the Resolution (not used)**")
    input5 = await bot.listen(editable.chat.id)

    try:
        xv = raw_text4.split('&')

        mm = "WinnersInstitute"

        for t in xv:
            if t.strip() == "":
                continue

            hdr11 = hdr1

            res4 = requests.get(
                f"https://winnersinstituteapi.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3?"
                f"topicid={t}&start=-1&courseid={raw_text2}&subjectid={raw_text3}",
                headers=hdr11
            ).json()

            topicid = res4["data"]

            for data in topicid:
                b64 = data["download_link"] if data["download_link"] else data["pdf_link"]
                tid = data["Title"]

                key = "638udh3829162018".encode("utf8")
                iv = "fedcba9876543210".encode("utf8")

                ciphertext = bytearray.fromhex(b64decode(b64.encode()).hex())
                cipher = AES.new(key, AES.MODE_CBC, iv)
                plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
                final_url = plaintext.decode('utf-8')

                with open(f"{mm}.txt", "a") as f:
                    f.write(f"{tid}:{final_url}\n")

        await m.reply_document(f"{mm}.txt")

    except Exception as e:
        await m.reply_text(str(e))

    await m.reply_text("Done")
