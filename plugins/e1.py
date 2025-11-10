#  MIT License
#  Code edited By Cryptostark

import requests
import json
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
import os

# Pyrogram v2 fix: remove filters.edited
# No "~filters.edited" needed now

from pyrogram import Client as bot

@bot.on_message(filters.command(["e1"]))
async def account_login(bot: Client, m: Message):
    try:
        editable = await m.reply_text(
            "Send **ID & Password** like this:\n\n`ID*Password`"
        )

        input1: Message = await bot.listen(editable.chat.id)
        raw_text = input1.text

        if "*" not in raw_text:
            return await editable.edit("Wrong format. Use:  `ID*Password`")

        email = raw_text.split("*")[0]
        password = raw_text.split("*")[1]
        await input1.delete(True)

        login_url = "https://e1coachingcenterapi.classx.co.in/post/userLogin"

        hdr = {
            "Auth-Key": "appxapi",
            "User-Id": "-2",
            "Authorization": "",
            "User_app_category": "",
            "Language": "en",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.9.1"
        }

        info = {"email": email, "password": password}

        scraper = cloudscraper.create_scraper()
        resp = scraper.post(login_url, data=info, headers=hdr).content
        output = json.loads(resp)

        userid = output["data"]["userid"]
        token = output["data"]["token"]

        hdr1 = {
            "Host": "e1coachingcenterapi.classx.co.in",
            "Client-Service": "Appx",
            "Auth-Key": "appxapi",
            "User-Id": userid,
            "Authorization": token
        }

        await editable.edit("✅ **Login Successful!**")

        res1 = requests.get(
            f"https://e1coachingcenterapi.classx.co.in/get/mycourse?userid={userid}",
            headers=hdr1
        )

        batches = res1.json()['data']
        cool = ""
        FFF = "**BATCH-ID - BATCH NAME**"

        for data in batches:
            aa = f"```{data['id']}``` - **{data['course_name']}**\n\n"
            if len(cool + aa) > 4096:
                await editable.edit(cool)
                cool = ""
            cool += aa

        await editable.edit(f"**You have these batches:**\n\n{FFF}\n\n{cool}")

        # Ask batch id
        ask = await m.reply_text("**Send Batch ID**")
        input2: Message = await bot.listen(ask.chat.id)
        batch_id = input2.text

        # subject list
        html = scraper.get(
            f"https://e1coachingcenterapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
            headers=hdr1
        ).content
        subject_list = json.loads(html)["data"]

        await m.reply_text(str(subject_list))

        ask2 = await m.reply_text("**Enter Subject ID shown above**")
        input3: Message = await bot.listen(ask2.chat.id)
        subj_id = input3.text

        # topics
        res3 = requests.get(
            f"https://e1coachingcenterapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={subj_id}",
            headers=hdr1
        )
        topics = res3.json()['data']

        vj = "&".join(str(t["topicid"]) for t in topics)

        cool1 = ""
        BBB = "**TOPIC-ID - TOPIC - VIDEOS**"

        for data in topics:
            tname = data["topic_name"]
            tid = data["topicid"]
            count = len(tid)  # not actual count but keeping original logic
            line = f"```{tid}``` - **{tname} - ({count})**\n"
            if len(cool1 + line) > 4096:
                await m.reply_text(cool1)
                cool1 = ""
            cool1 += line

        await m.reply_text(f"**Batch Details:**\n\n{BBB}\n\n{cool1}")

        ask3 = await m.reply_text(
            f"Send Topic IDs like:\n`1&2&3`\n\nFull batch:\n```{vj}```"
        )
        input4 = await bot.listen(ask3.chat.id)
        topic_ids = input4.text.split("&")

        ask4 = await m.reply_text("**Send Resolution**")
        input5 = await bot.listen(ask4.chat.id)
        resolution = input5.text

        mm = "E1-Coaching-Center.txt"
        if os.path.exists(mm):
            os.remove(mm)

        # process topics
        for t in topic_ids:
            res4 = requests.get(
                f"https://e1coachingcenterapi.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3?topicid={t}&start=-1&conceptid=1&courseid={batch_id}&subjectid={subj_id}",
                headers=hdr1
            ).json()

            topic_content = res4["data"]

            key = "638udh3829162018".encode("utf8")
            iv = "fedcba9876543210".encode("utf8")

            for data in topic_content:
                enc = data["embed_url"] or data["pdf_link"]

                cipherbytes = bytearray.fromhex(b64decode(enc.encode()).hex())
                cipher = AES.new(key, AES.MODE_CBC, iv)
                plain = unpad(cipher.decrypt(cipherbytes), AES.block_size)
                final_url = plain.decode("utf-8")

                title = data["Title"]

                with open(mm, "a") as f:
                    f.write(f"{title}:{final_url}\n")

        await m.reply_document(mm)
        await m.reply_text("✅ **Done**")

    except Exception as e:
        await m.reply_text(f"❌ Error: `{str(e)}`")
