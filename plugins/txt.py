#  MIT License
#  Code edited By Cryptostark

import urllib
import urllib.parse
import requests
import json
from pyromod import listen
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram import Client as bot
import os
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

@bot.on_message(filters.command(["txt"]))
async def account_login(bot: Client, m: Message):
    try:
        # ASK INSTITUTE
        msg = await m.reply_text(
            "Copy any one:\n\n"
            "**Ankit With Rojgar**: `rozgarapinew.teachx.in`\n"
            "**The Last Exam**: `lastexamapi.teachx.in`\n"
            "**The Mission Institute**: `missionapi.appx.co.in`"
        )

        input01: Message = await bot.listen(msg.chat.id)
        Ins = input01.text.strip()

        # LOGIN ASK
        editable = await m.reply_text(
            "Send **ID*Password**"
        )

        login_url = f"https://{Ins}/post/login"

        hdr = {
            "Client-Service": "Appx",
            "Auth-Key": "appxapi",
            "User-ID": "-2",
            "Authorization": "",
            "User_app_category": "",
            "Language": "en",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "okhttp/4.9.1"
        }

        # CREDENTIAL INPUT
        input1: Message = await bot.listen(editable.chat.id)
        raw = input1.text
        await input1.delete()

        email, password = raw.split("*")

        info = {"email": email, "password": password}

        # LOGIN
        res = requests.post(login_url, data=info, headers=hdr).content
        output = json.loads(res)

        userid = output["data"]["userid"]
        token = output["data"]["token"]

        # SELECT HEADER BASED ON SITE
        hdr1 = {
            "Client-Service": "Appx",
            "Auth-Key": "appxapi",
            "User-ID": userid,
            "Authorization": token,
            "User_app_category": "",
            "Language": "en",
            "Host": Ins,
            "User-Agent": "okhttp/4.9.1"
        }

        await editable.edit("✅ **Login Successful**")

        # FETCH BATCHES
        res1 = requests.get(
            f"https://{Ins}/get/mycourse?userid={userid}",
            headers=hdr1
        )
        b_data = res1.json()["data"]

        cool = ""
        FFF = "**BATCH-ID - BATCH NAME**"

        for d in b_data:
            aa = f"```{d['id']}``` - **{d['course_name']}**\n\n"
            if len(cool + aa) > 4096:
                await m.reply_text(cool)
                cool = ""
            cool += aa

        await editable.edit(f"{FFF}\n\n{cool}")

        # ASK BATCH ID
        ask = await m.reply_text("Send **Batch ID**")
        input2 = await bot.listen(ask.chat.id)
        batch_id = input2.text.strip()
        await input2.delete()
        await ask.delete()

        # SUBJECT LIST
        res2 = requests.get(
            f"https://{Ins}/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
            headers=hdr1
        ).json()

        subj_data = res2["data"]

        subj_str = ""
        subj_ids = ""

        for s in subj_data:
            subj_str += f"```{s['subjectid']}``` - **{s['subject_name']}**\n\n"
            subj_ids += f"{s['subjectid']}&"

        await m.reply_text(subj_str)

        ask2 = await m.reply_text(
            f"Send **Subject IDs**\n\nFull List:\n```{subj_ids}```"
        )
        input3 = await bot.listen(ask2.chat.id)
        subject_id = input3.text.strip()
        await input3.delete()
        await ask2.delete()

        # TOPIC LIST
        res3 = requests.get(
            f"https://{Ins}/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={subject_id}",
            headers=hdr1
        ).json()

        topics = res3["data"]

        topic_ids = ""
        topic_text = ""

        for t in topics:
            tid = t["topicid"]
            name = t["topic_name"]
            topic_ids += f"{tid}&"
            topic_text += f"```{tid}``` - **{name}**\n\n"

        await m.reply_text(f"Topics:\n\n{topic_text}")

        # ASK TOPIC IDS
        ask4 = await m.reply_text(
            f"Send Topic IDs like `1&2&3`\n\nFull List:\n```{topic_ids}```"
        )
        input4 = await bot.listen(ask4.chat.id)
        raw_topic_ids = input4.text
        await input4.delete()

        # RESOLUTION ASK
        ask5 = await m.reply_text("Send Resolution")
        input5 = await bot.listen(ask5.chat.id)
        await ask5.delete()

        # START EXTRACTING
        xv = raw_topic_ids.split("&")

        final_name = "TeachX-Extracted.txt"
        if os.path.exists(final_name):
            os.remove(final_name)

        for t in xv:
            t = t.strip()
            if not t:
                continue

            # API route selection based on host
            base_url = (
                f"https://{Ins}/get/livecourseclassbycoursesubtopconceptapiv3"
            )

            res4 = requests.get(
                f"{base_url}?topicid={t}&start=-1&courseid={batch_id}&subjectid={subject_id}",
                headers=hdr1
            ).json()

            topicid = res4["data"]

            for data in topicid:
                enc = data["download_link"] or data["pdf_link"]

                # AES DECODE
                key = "638udh3829162018".encode()
                iv = "fedcba9876543210".encode()

                cipher = AES.new(key, AES.MODE_CBC, iv)
                ciphertext = bytearray.fromhex(b64decode(enc.encode()).hex())
                plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
                url = plaintext.decode()

                title = data["Title"]
                title = title.replace(":", " ").replace("/", " ").strip()

                with open(final_name, "a") as f:
                    f.write(f"{title}:{url}\n")

        await m.reply_document(final_name)
        await m.reply_text("✅ Done")

        os.remove(final_name)

    except Exception as e:
        await m.reply_text(f"❌ Error: `{str(e)}`")
