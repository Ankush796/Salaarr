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
import cloudscraper
import os
import time


@bot.on_message(filters.command(["samyak"]))
async def account(bot: Client, m: Message):
    try:
        s = requests.Session()

        editable = await m.reply_text(
            "Send **ID & Password** like this:\n\n`ID*Password`"
        )

        input1: Message = await bot.listen(editable.chat.id)
        raw = input1.text
        await input1.delete()

        if "*" not in raw:
            return await editable.edit("Format galat hai. Use: `ID*Password`")

        email = raw.split("*")[0]
        password = raw.split("*")[1]

        login_url = "https://samyak.teachx.in/pages/login2"

        hdr = {
            "Auth-Key": "appxapi",
            "User-Id": "-2",
            "Authorization": "",
            "User_app_category": "",
            "Language": "en",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "okhttp/4.9.1"
        }

        info = {"email": email, "password": password}

        res = s.post(login_url, data=info, headers=hdr)
        output = res.json()

        userid = output["data"]["userid"]
        token = output["data"]["token"]

        hdr1 = {
            'Authorization': token,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12)',
            'User-ID': userid,
            'auth-key': 'appxapi',
            'client-service': 'Appx'
        }

        await editable.edit("✅ **Login Successful**")

        # BATCH LIST
        res1 = s.get(
            f'https://samyakapi.teachx.in/get/mycourseweb?userid={userid}',
            headers=hdr1
        )
        batches = res1.json()['data']

        cool = ""
        FFF = "**BATCH-ID - BATCH NAME**"

        for b in batches:
            aa = f"```{b['id']}``` - **{b['course_name']}**\n\n"
            if len(cool + aa) > 4096:
                await m.reply_text(cool)
                cool = ""
            cool += aa

        await editable.edit(f"**You have these batches:**\n\n{FFF}\n\n{cool}")

        # ASK FOR BATCH ID
        ask = await m.reply_text("**Send Batch ID**")
        input2 = await bot.listen(ask.chat.id)
        batch_id = input2.text
        await input2.delete()
        await ask.delete()

        # SUBJECTS
        scraper = cloudscraper.create_scraper()
        html = scraper.get(
            f"https://samyakapi.teachx.in/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
            headers=hdr1
        ).content

        subj_data = json.loads(html)["data"]

        vj = ""
        cool = ""

        for sub in subj_data:
            sid = sub["subjectid"]
            cool += f"```{sid}``` - **{sub['subject_name']}**\n\n"
            vj += f"{sid}&"

        await m.reply_text(cool)

        ask2 = await m.reply_text(
            f"Send **Subject IDs** like `1&2&3`\n\nFull batch:\n```{vj}```"
        )

        input3 = await bot.listen(ask2.chat.id)
        subject_ids = input3.text
        await input3.delete()
        await ask2.delete()

        # -----------------------------
        # START EXTRACTION
        # -----------------------------

        prog = await editable.edit("📥 Extracting links... Please wait")

        filename = None  # will create once batch info extracted

        xv = subject_ids.split("&")

        for sid in xv:
            sid = sid.strip()
            if not sid:
                continue

            # GET TOPICS
            res3 = s.get(
                f"https://samyakapi.teachx.in/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={sid}",
                headers=hdr1
            )

            topics = res3.json()['data']

            for topic in topics:
                t_name = topic["topic_name"]
                t_id = topic["topicid"]

                # FIRST VALID TOPIC → CREATE FILENAME
                if filename is None:
                    filename = f"SamayakIAS - {t_name}.txt"
                    if os.path.exists(filename):
                        os.remove(filename)

                hdr2 = {
                    'Authorization': token,
                    'User-Agent': 'Mozilla/5.0',
                    'User-ID': userid,
                    'auth-key': 'appxapi',
                    'client-service': 'Appx'
                }

                url = (
                    "https://samyakapi.teachx.in/get/livecourseclassbycoursesubtopconceptapiv3"
                    f"?courseid={batch_id}&subjectid={sid}&topicid={t_id}&start=-1"
                )

                res4 = s.get(url, headers=hdr2).json()
                entries = res4["data"]

                for e in entries:
                    title = e["Title"]

                    if e["download_link"]:
                        link = e["download_link"]
                        inf = {"link": link}
                        mid = s.post(
                            "https://samyak.teachx.in/pages/decrypt",
                            headers=hdr,
                            data=inf
                        ).text

                        final_link = "https://cdn.jwplayer.com/manifests/" + mid

                        with open(filename, "a") as f:
                            f.write(f"{title}:{final_link}\n")

                    if e["pdf_link"]:
                        inf = {"link": e["pdf_link"]}
                        pdf_url = s.post(
                            "https://samyak.teachx.in/pages/decrypt",
                            headers=hdr,
                            data=inf
                        ).text

                        with open(filename, "a") as f:
                            f.write(f"{title}:{pdf_url}\n")

        await prog.delete()

        if filename and os.path.exists(filename):
            await m.reply_document(filename)
            os.remove(filename)

    except Exception as e:
        await m.reply_text(f"❌ Error: `{str(e)}`")
