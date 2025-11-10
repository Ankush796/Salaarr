#  MIT License
#  Code edited By Cryptostark

import json
import os

import requests
import cloudscraper
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram import Client as bot


@bot.on_message(filters.command(["vidya"]) & ~filters.edited)
async def account_login(bot: Client, m: Message):
    # Globals/flags (original logic preserve)
    global cancel
    cancel = False

    # Step 1: Login prompt
    editable = await m.reply_text(
        "Send **ID & Password** is format:  `ID*Password`"
    )

    # Login endpoint + headers
    login_url = "https://vidyabiharapi.teachx.in/post/userLogin"
    hdr = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Authorization": "",
        "User_app_category": "",
        "Language": "en",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "233",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "okhttp/4.9.1",
    }

    # Take creds
    input1: Message = await bot.listen(editable.chat.id)
    raw_text = input1.text
    info = {"email": "", "password": ""}

    try:
        info["email"] = raw_text.split("*")[0]
        info["password"] = raw_text.split("*")[1]
    except Exception:
        await editable.edit("❌ Format galat hai. Use:  `ID*Password`")
        return
    finally:
        await input1.delete(True)

    # Do login
    scraper = cloudscraper.create_scraper()
    res = scraper.post(login_url, data=info, headers=hdr).content
    output = json.loads(res)

    userid = output["data"]["userid"]
    token = output["data"]["token"]

    hdr1 = {
        "Host": "vidyabiharapi.teachx.in",
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": userid,
        "Authorization": token,
    }

    await editable.edit("✅ **Login Successful**")

    # Step 2: Show courses/batches
    res1 = requests.get(
        f"https://vidyabiharapi.teachx.in/get/mycourse?userid={userid}",
        headers=hdr1,
    )
    b_data = res1.json()["data"]

    cool = ""
    FFF = "**BATCH-ID - BATCH NAME - INSTRUCTOR**"
    for data in b_data:
        aa = f" ```{data['id']}```      - **{data['course_name']}**\n\n"
        if len(f"{cool}{aa}") > 4096:
            cool = ""
        cool += aa

    await editable.edit(f'{"**You have these batches :-**"}\n\n{FFF}\n\n{cool}')

    # Step 3: Ask batch id
    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)

    # Subjects for batch
    html = scraper.get(
        f"https://vidyabiharapi.teachx.in/get/allsubjectfrmlivecourseclass?courseid={raw_text2}",
        headers=hdr1,
    ).content
    output0 = json.loads(html)
    subjID = output0["data"]
    await m.reply_text(subjID)

    # Step 4: Ask subject id
    editable1 = await m.reply_text("**Enter the Subject Id shown above**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)

    # Topics list (FIX: URL concat tha tootaa hua — join kiya)
    res3 = requests.get(
        f"https://vidyabiharapi.teachx.in/get/alltopicfrmlivecourseclass?courseid={raw_text2}&subjectid={raw_text3}",
        headers=hdr1,
    )
    b_data2 = res3.json()["data"]

    # Build helper strings
    vj = ""
    vp = ""
    cool1 = ""
    for data in b_data2:
        tids = data["topicid"]
        tn = data["topic_name"]
        idid = f"{tids}&"
        tns = f"{tn}&"
        if len(f"{vj}{idid}") > 4096:
            vj = ""
        if len(f"{vp}{tns}") > 4096:
            vp = ""
        vj += idid
        vp += tns

    for data in b_data2:
        t_name = data["topic_name"]
        tid = data["topicid"]
        zz = len(tid)
        BBB = "**TOPIC-ID    - TOPIC     - VIDEOS**\n"
        hh = f"```{tid}```     - **{t_name} - ({zz})**\n"
        if len(f"{cool1}{hh}") > 4096:
            cool1 = ""
        cool1 += hh

    await m.reply_text(f"Batch details of **{t_name}** are:\n\n{BBB}\n\n{cool1}")

    # Step 5: Ask which topic ids to download
    editable = await m.reply_text(
        "Now send the **Topic IDs** to Download\n\n"
        "Send like this **1&2&3&4** so on\n"
        "or copy paste or edit **below ids** according to you :\n\n"
        f"**Enter this to download full batch :-**\n```{vj}```"
    )
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)

    # (Original code asked resolution but didn't use it — keep for parity)
    editable3 = await m.reply_text("**Now send the Resolution**")
    input5: Message = await bot.listen(editable.chat.id)
    raw_text5 = input5.text  # not used, original behavior preserved
    await input5.delete(True)

    mm = "Vidya-Bihar-Institute"  # file prefix

    try:
        # Iterate selected topics
        xv = raw_text4.split("&")
        for y in range(0, len(xv)):
            t = xv[y]

            hdr11 = {
                "Host": "vidyabiharapi.teachx.in",
                "Client-Service": "Appx",
                "Auth-Key": "appxapi",
                "User-Id": userid,
                "Authorization": token,
            }

            res4 = requests.get(
                f"https://vidyabiharapi.teachx.in/get/livecourseclassbycoursesubtopconceptapiv3?"
                f"topicid={t}&start=-1&courseid={raw_text2}&subjectid={raw_text3}",
                headers=hdr11,
            ).json()

            topicid = res4["data"]

            # Decrypt & save links
            for data in topicid:
                b64 = data["download_link"] if data["download_link"] else data["pdf_link"]
                tid_title = data["Title"]

                # AES-CBC decrypt (original static key/iv retained)
                key = "638udh3829162018".encode("utf8")
                iv = "fedcba9876543210".encode("utf8")
                ciphertext = bytearray.fromhex(b64decode(b64.encode()).hex())
                cipher = AES.new(key, AES.MODE_CBC, iv)
                plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
                url = plaintext.decode("utf-8")

                with open(f"{mm}.txt", "a") as f:
                    f.write(f"{tid_title}:{url}\n")

        # Send collected file
        if os.path.exists(f"{mm}.txt"):
            await m.reply_document(f"{mm}.txt")
        else:
            await m.reply_text("⚠️ Koi link generate nahi hua.")

    except Exception as e:
        await m.reply_text(str(e))

    await m.reply_text("Done")
