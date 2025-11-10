#  MIT License
#  Code edited By Cryptostark

import urllib
import urllib.parse
import requests
import json
import subprocess
from pyromod import listen
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram import Client as bot
import cloudscraper
import os

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

def decode(tn):
    key = "638udh3829162018".encode("utf8")
    iv = "fedcba9876543210".encode("utf8")
    ciphertext = bytearray.fromhex(b64decode(tn.encode()).hex())
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode('utf-8')


@bot.on_message(filters.command(["rgvikramjeet"]))
async def account_login(bot: Client, m: Message):

    s = requests.Session()
    editable = await m.reply_text(
        "Send **ID & Password** like this:\n\n`ID*Password`"
    )

    input1: Message = await bot.listen(editable.chat.id)
    raw = input1.text
    await input1.delete()

    if "*" not in raw:
        return await editable.edit("Wrong Format. Use: `ID*Password`")

    email = raw.split("*")[0]
    pwd = raw.split("*")[1]

    login_url = "https://rgvikramjeetapi.classx.co.in/post/userLogin"
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

    info = {"email": email, "password": pwd}

    scraper = cloudscraper.create_scraper()
    res = scraper.post(login_url, data=info, headers=hdr).content
    output = json.loads(res)

    userid = output["data"]["userid"]
    token = output["data"]["token"]

    hdr1 = {
        "Host": "rgvikramjeetapi.classx.co.in",
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": userid,
        "Authorization": token
    }

    await editable.edit("✅ **Login Successful**")

    # batches
    res1 = s.get(
        f"https://rgvikramjeetapi.classx.co.in/get/mycourse?userid={userid}",
        headers=hdr1
    )
    batches = res1.json()['data']

    cool = ""
    FFF = "**BATCH-ID - BATCH NAME - INSTRUCTOR**"

    for b in batches:
        aa = f"```{b['id']}``` - **{b['course_name']}**\n\n"
        if len(cool + aa) > 4096:
            await m.reply_text(cool)
            cool = ""
        cool += aa

    await editable.edit(f"**You have these batches:**\n\n{FFF}\n\n{cool}")

    editable1 = await m.reply_text("**Send Batch ID**")
    input2 = await bot.listen(editable1.chat.id)
    batch_id = input2.text
    await input2.delete()
    await editable1.delete()

    # course title
    html = scraper.get(
        f"https://rgvikramjeetapi.classx.co.in/get/course_by_id?id={batch_id}",
        headers=hdr1
    ).json()
    course_title = html["data"][0]["course_name"]

    # all subjects
    html = scraper.get(
        f"https://rgvikramjeetapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
        headers=hdr1
    ).content
    subj_data = json.loads(html)["data"]

    cool = ""
    vj = ""

    for sub in subj_data:
        subjid = sub["subjectid"]
        aa = f"```{subjid}``` - **{sub['subject_name']}**\n\n"
        vj += f"{subjid}&"
        cool += aa

    await editable.edit(cool)

    editable2 = await m.reply_text(
        f"Send **Subject IDs** like:\n`1&2&3`\n\nFull batch:\n```{vj}```"
    )

    input3 = await bot.listen(editable2.chat.id)
    subject_ids = input3.text
    await input3.delete()
    await editable2.delete()

    prog = await editable.edit("📥 Extracting video links... Please wait")

    try:
        mm = "Rgvikramjeet"
        filename = f"{mm} - {course_title}.txt"

        if os.path.exists(filename):
            os.remove(filename)

        xv = subject_ids.split("&")

        for sid in xv:
            sid = sid.strip()
            if not sid:
                continue

            # topics
            res3 = requests.get(
                f"https://rgvikramjeetapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={sid}",
                headers=hdr1
            )
            topics = res3.json()['data']

            for t in topics:
                topic_name = t["topic_name"]
                topic_id = t["topicid"]

                hdr2 = {
                    "Host": "rgvikramjeetapi.classx.co.in",
                    "Client-Service": "Appx",
                    "Auth-Key": "appxapi",
                    "User-Id": userid,
                    "Authorization": token
                }

                # get concepts
                par = {
                    'courseid': batch_id,
                    'subjectid': sid,
                    'topicid': topic_id,
                    'start': '-1'
                }

                res6 = requests.get(
                    'https://rgvikramjeetapi.classx.co.in/get/allconceptfrmlivecourseclass',
                    params=par,
                    headers=hdr2
                ).json()

                concepts = res6['data']

                for c in concepts:
                    cid = c["conceptid"]

                    par2 = {
                        'courseid': batch_id,
                        'subjectid': sid,
                        'topicid': topic_id,
                        'conceptid': cid,
                        'start': '-1'
                    }

                    res4 = requests.get(
                        'https://rgvikramjeetapi.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3',
                        params=par2,
                        headers=hdr2
                    ).json()

                    try:
                        for entry in res4["data"]:
                            tn = entry["download_link"]
                            title = entry["Title"]

                            url = decode(tn)

                            with open(filename, "a") as f:
                                f.write(f"{title}:{url}\n")

                    except Exception as e:
                        await m.reply_text(f"{title} : {e}")
                        continue

        await prog.delete()
        await m.reply_document(filename, caption=f"```{mm} - {course_title}```")

        os.remove(filename)

    except Exception as e:
        await m.reply_text(str(e))
