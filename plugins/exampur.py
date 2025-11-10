#  MIT License
#  Code edited By Cryptostark

import urllib.parse
import requests
import json
import cloudscraper
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram import Client as bot
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import os


@bot.on_message(filters.command(["exampur"]))
async def account_login(bot: Client, m: Message):
    try:
        editable = await m.reply_text(
            "Send **ID & Password** like this:\n\n`ID*Password`"
        )

        input1: Message = await bot.listen(editable.chat.id)
        raw_text = input1.text

        if "*" not in raw_text:
            return await editable.edit("Wrong format! Use:  `ID*Password`")

        email = raw_text.split("*")[0]
        password = raw_text.split("*")[1]
        await input1.delete(True)

        login_url = "https://auth.exampurcache.xyz/auth/login"

        hdr = {
            "appauthtoken": "no_token",
            "User-Agent": "Dart/2.15(dart:io)",
            "content-type": "application/json; charset=UTF-8",
            "Accept-Encoding": "gzip",
            "host": "auth.exampurcache.xyz"
        }

        info = {
            "phone_ext": "91",
            "phone": "",
            "email": email,
            "password": password
        }

        scraper = cloudscraper.create_scraper()
        res = scraper.post(login_url, json=info, headers=hdr).content
        output = json.loads(res)

        token = output["data"]["authToken"]

        hdr1 = {
            "appauthtoken": token,
            "User-Agent": "Dart/2.15(dart:io)",
            "Accept-Encoding": "gzip",
            "host": "auth.exampurcache.xyz"
        }

        await editable.edit("✅ **Login Successful**")

        # Batches
        res1 = requests.get("https://auth.exampurcache.xyz/mycourses", headers=hdr1)
        batches = res1.json()['data']

        cool = ""
        FFF = "**BATCH-ID - BATCH NAME**"

        for data in batches:
            aa = f"```{data['_id']}``` - **{data['title']}**\n\n"
            if len(cool + aa) > 4096:
                await editable.edit(cool)
                cool = ""
            cool += aa

        await editable.edit(f"**Your Batches:**\n\n{FFF}\n\n{cool}")

        ask = await m.reply_text("**Send Batch ID**")
        input2 = await bot.listen(ask.chat.id)
        batch_id = input2.text

        # Subjects
        html = scraper.get(
            f"https://auth.exampurcache.xyz/course_subject/{batch_id}",
            headers=hdr1
        ).content
        subj_data = json.loads(html)["data"]

        vj = "&".join(str(s["_id"]) for s in subj_data)
        await m.reply_text(vj)

        ask2 = await m.reply_text(
            f"Send Topic IDs like `1&2&3`\n\nFull batch:\n```{vj}```"
        )
        input4 = await bot.listen(ask2.chat.id)
        topic_ids = input4.text.split("&")

        mm = "Exampur.txt"
        if os.path.exists(mm):
            os.remove(mm)

        # Process chapters + videos
        for t in topic_ids:
            chapter_resp = requests.get(
                f"https://auth.exampurcache.xyz/course_material/chapter/{t}/{batch_id}",
                headers=hdr1
            ).json()

            chapters = chapter_resp["data"]

            for chap in chapters:
                encoded = urllib.parse.quote(chap, safe="")
                chapter_clean = (
                    encoded.replace("%28", "(")
                    .replace("%29", ")")
                    .replace("%26", "&")
                )

                material_resp = requests.get(
                    f"https://auth.exampurcache.xyz/course_material/material/{t}/{batch_id}/{chapter_clean}",
                    headers=hdr1
                ).json()

                files = material_resp["data"]

                for v in files:
                    title = v["title"]
                    link = v["video_link"]

                    with open(mm, "a") as f:
                        f.write(f"{title}:{link}\n")

        await m.reply_document(mm)
        await m.reply_text("✅ Done")

    except Exception as e:
        await m.reply_text(f"❌ Error: `{str(e)}`")
