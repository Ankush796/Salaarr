# MIT License
# Cleaned & Fixed Ocean-Gurukul Extractor — Cryptostark Upgrade

import json
import requests
import cloudscraper
from pyromod import listen
from pyrogram import Client as bot, filters
from pyrogram.types import Message
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
import os


def decrypt(enc):
    """Decrypt AES encoded ocean-links"""
    try:
        key = "638udh3829162018".encode("utf8")
        iv = "fedcba9876543210".encode("utf8")
        ciphertext = bytearray.fromhex(b64decode(enc.encode()).hex())
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return plaintext.decode("utf-8")
    except:
        return "Invalid/Encrypted"


@bot.on_message(filters.command("ocean"))
async def ocean_handler(bot, m: Message):

    editable = await m.reply_text(
        "Send **ID & Password** like this:\n\n`ID*Password`"
    )

    inp: Message = await bot.listen(editable.chat.id)
    raw = inp.text

    if "*" not in raw:
        return await editable.edit("❌ Wrong format! Use `ID*Password`")

    email = raw.split("*")[0]
    password = raw.split("*")[1]
    await inp.delete()

    login_url = "https://oceangurukulsapi.classx.co.in/post/userLogin"

    hdr = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "okhttp/4.9.1",
    }

    scraper = cloudscraper.create_scraper()
    res = scraper.post(login_url, data={"email": email, "password": password}, headers=hdr).content
    data = json.loads(res)

    user_id = data["data"]["userid"]
    token = data["data"]["token"]

    hdr_auth = {
        "Host": "oceangurukulsapi.classx.co.in",
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": user_id,
        "Authorization": token
    }

    await editable.edit("✅ **Login Successful**")

    # ------------------------- BATCH LIST -------------------------
    batches = requests.get(
        f"https://oceangurukulsapi.classx.co.in/get/mycourse?userid={user_id}",
        headers=hdr_auth
    ).json()["data"]

    text = ""
    for b in batches:
        text += f"```{b['id']}``` — **{b['course_name']}**\n\n"

    await editable.edit(f"**Your Batches:**\n\n{text}")

    ask1 = await m.reply_text("✅ Send Batch ID")
    batch_id = (await bot.listen(ask1.chat.id)).text

    # ------------------------- SUBJECT LIST -------------------------
    subj_resp = scraper.get(
        f"https://oceangurukulsapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
        headers=hdr_auth
    ).json()["data"]

    sub_list = ""
    sub_ids = ""

    for s in subj_resp:
        sid = s["subjectid"]
        name = s["subject_name"]
        sub_list += f"```{sid}``` — **{name}**\n"
        sub_ids += f"{sid}&"

    ask2 = await m.reply_text(
        f"**Subjects:**\n\n{sub_list}\n\nSend IDs:\n```{sub_ids}```"
    )
    subject_ids = (await bot.listen(ask2.chat.id)).text.split("&")

    # ------------------------- OUTPUT FILE -------------------------
    file_name = "Ocean-Gurukul.txt"
    if os.path.exists(file_name):
        os.remove(file_name)

    prog = await m.reply_text("📥 Extracting links... Please wait...")

    # ------------------------- TOPICS + LINKS -------------------------
    try:
        for sid in subject_ids:
            sid = sid.strip()
            if not sid:
                continue

            topic_resp = requests.get(
                f"https://oceangurukulsapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={sid}",
                headers=hdr_auth
            ).json()["data"]

            for topic in topic_resp:
                tid = topic["topicid"]

                video_resp = requests.get(
                    f"https://oceangurukulsapi.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3?courseid={batch_id}&subjectid={sid}&topicid={tid}&start=-1",
                    headers=hdr_auth
                ).json()["data"]

                for v in video_resp:
                    title = v["Title"]

                    # Video link
                    if v["download_link"]:
                        url = decrypt(v["download_link"])
                        with open(file_name, "a") as f:
                            f.write(f"{title}:{url}\n")

                    # PDF link
                    if v["pdf_link"]:
                        url = decrypt(v["pdf_link"])
                        with open(file_name, "a") as f:
                            f.write(f"{title}:{url}\n")

        await prog.delete()
        await m.reply_document(file_name, caption="✅ Ocean Gurukul Extracted")
    except Exception as e:
        await m.reply_text(f"❌ Error: {str(e)}")
