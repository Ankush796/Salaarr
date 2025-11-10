# MIT License
# Fixed & Cleaned Version — Cryptostark Upgrade

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


def decode(enc):
    """Decrypt mgconcept AES encoded URLs"""
    key = "638udh3829162018".encode("utf8")
    iv = "fedcba9876543210".encode("utf8")
    ciphertext = bytearray.fromhex(b64decode(enc.encode()).hex())
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return pt.decode("utf-8")


@bot.on_message(filters.command("mgconcept"))
async def mgconcept_handler(bot, m: Message):

    editable = await m.reply_text(
        "Send **ID & Password** like this:\n\n`ID*Password`"
    )

    # USER LOGIN INPUT
    inp: Message = await bot.listen(editable.chat.id)
    raw = inp.text
    if "*" not in raw:
        return await editable.edit("❌ Wrong format! Use: `ID*Password`")

    email = raw.split("*")[0]
    password = raw.split("*")[1]
    await inp.delete(True)

    login_url = "https://mgconceptapi.classx.co.in/post/userLogin"

    headers = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "okhttp/4.9.1"
    }

    scraper = cloudscraper.create_scraper()
    res = scraper.post(login_url, data={"email": email, "password": password}, headers=headers).content
    output = json.loads(res)

    user_id = output["data"]["userid"]
    token = output["data"]["token"]

    hdr_auth = {
        "Host": "mgconceptapi.classx.co.in",
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": user_id,
        "Authorization": token
    }

    await editable.edit("✅ **Login Successful**")

    # FETCH COURSES
    course_list = requests.get(
        f"https://mgconceptapi.classx.co.in/get/mycourse?userid={user_id}",
        headers=hdr_auth
    ).json()["data"]

    text = ""
    for c in course_list:
        text += f"```{c['id']}``` — **{c['course_name']}**\n\n"

    await editable.edit(f"**Your Batches:**\n\n{text}")

    ask1 = await m.reply_text("✅ Send Batch ID")
    batch_id = (await bot.listen(ask1.chat.id)).text

    # GET COURSE NAME
    course_title = requests.get(
        f"https://mgconceptapi.classx.co.in/get/course_by_id?id={batch_id}",
        headers=hdr_auth
    ).json()["data"][0]["course_name"]

    # GET SUBJECTS
    subj_resp = scraper.get(
        f"https://mgconceptapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
        headers=hdr_auth
    ).json()["data"]

    sub_list = ""
    sub_ids = ""

    for sdata in subj_resp:
        sid = sdata["subjectid"]
        sname = sdata["subject_name"]
        sub_list += f"```{sid}``` — **{sname}**\n"
        sub_ids += f"{sid}&"

    ask2 = await m.reply_text(
        f"**Subjects:**\n\n{sub_list}\n\nSend Subject IDs:\n```{sub_ids}```"
    )

    subject_ids = (await bot.listen(ask2.chat.id)).text.split("&")

    # OUTPUT TXT
    file_name = f"MgConcept-{course_title}.txt"
    if os.path.exists(file_name):
        os.remove(file_name)

    prog = await m.reply_text("📥 Extracting links, please wait...")

    try:
        for sid in subject_ids:
            sid = sid.strip()
            if not sid:
                continue

            # GET TOPICS
            topics = requests.get(
                f"https://mgconceptapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={sid}",
                headers=hdr_auth
            ).json()["data"]

            for topic in topics:
                topic_id = topic["topicid"]

                # GET VIDEO LINKS FOR EACH TOPIC
                vresp = requests.get(
                    f"https://mgconceptapi.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3?courseid={batch_id}&subjectid={sid}&topicid={topic_id}&start=-1",
                    headers=hdr_auth
                ).json()["data"]

                for v in vresp:
                    title = v["Title"]

                    # decode video / pdf link
                    if v["download_link"]:
                        try:
                            real_url = decode(v["download_link"])
                        except:
                            real_url = "Invalid/Encrypted"
                        with open(file_name, "a") as f:
                            f.write(f"{title}:{real_url}\n")

                    if v["pdf_link"]:
                        try:
                            real_url = decode(v["pdf_link"])
                        except:
                            real_url = "Invalid/Encrypted"
                        with open(file_name, "a") as f:
                            f.write(f"{title}:{real_url}\n")

        await prog.delete()
        await m.reply_document(file_name, caption=f"✅ Extracted: `{course_title}`")

    except Exception as e:
        await m.reply_text(f"❌ Error: {str(e)}")
