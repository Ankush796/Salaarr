#  MIT License
#  Code edited By Cryptostark

import json
import requests
import cloudscraper
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from pyromod import listen  # to enable .listen()
from pyrogram import Client as bot, filters
from pyrogram.types import Message


def _aes_decode(b64: str) -> str:
    """Decode AES-CBC(base64→hex) string used by these APIs."""
    key = "638udh3829162018".encode("utf8")
    iv = "fedcba9876543210".encode("utf8")
    ciphertext = bytearray.fromhex(b64decode(b64.encode()).hex())
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode("utf-8")


@bot.on_message(filters.command(["winners"]))
async def account_login(client: bot, m: Message):
    # ---- login ----
    editable = await m.reply_text(
        "Send **ID & Password** is format:  `ID*Password`"
    )
    input1: Message = await client.listen(editable.chat.id)
    raw_text = input1.text or ""
    await input1.delete(True)

    if "*" not in raw_text:
        return await editable.edit("❌ Galat format! Use:  `ID*Password`")

    email, password = raw_text.split("*", 1)

    login_url = "https://winnersinstituteapi.classx.co.in/post/userLogin"
    hdr_login = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Authorization": "",
        "User_app_category": "",
        "Language": "en",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "okhttp/4.9.1",
    }

    scraper = cloudscraper.create_scraper()
    res = scraper.post(login_url, data={"email": email, "password": password}, headers=hdr_login).content
    try:
        output = json.loads(res)
        userid = output["data"]["userid"]
        token = output["data"]["token"]
    except Exception:
        return await editable.edit("❌ Login failed. Response invalid ya creds galat.")

    hdr_auth = {
        "Host": "winnersinstituteapi.classx.co.in",
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": userid,
        "Authorization": token,
    }

    await editable.edit("✅ **Login Successful**")

    # ---- list courses ----
    r1 = requests.get(
        f"https://winnersinstituteapi.classx.co.in/get/mycourse?userid={userid}",
        headers=hdr_auth,
    )
    data = r1.json().get("data", [])
    if not data:
        return await m.reply_text("Koi course nahi mila.")

    FFF = "**BATCH-ID - BATCH NAME**"
    chunks = []
    for d in data:
        chunks.append(f"```{d['id']}```  - **{d['course_name']}**")
    await editable.edit(f"**You have these batches :-**\n\n{FFF}\n\n" + "\n\n".join(chunks))

    # ---- ask batch id ----
    ask_batch = await m.reply_text("**Now send the Batch ID to Download**")
    inp_batch = await client.listen(ask_batch.chat.id)
    batch_id = (inp_batch.text or "").strip()
    await inp_batch.delete(True)

    # ---- subjects for batch ----
    html = scraper.get(
        f"https://winnersinstituteapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={batch_id}",
        headers=hdr_auth,
    ).content
    subj = json.loads(html).get("data", [])
    if not subj:
        return await m.reply_text("Is batch me subjects nahi mile.")

    # show topics list will be built after user picks subject
    subs_lines, subject_ids = [], []
    for s in subj:
        subs_lines.append(f"```{s['subjectid']}```  - **{s['subject_name']}**")
        subject_ids.append(str(s["subjectid"]))
    await m.reply_text("\n\n".join(subs_lines))

    ask_sub = await m.reply_text("**Enter the Subject Id shown above**")
    inp_sub = await client.listen(ask_sub.chat.id)
    subject_id = (inp_sub.text or "").strip()
    await inp_sub.delete(True)

    # ---- topics under subject ----
    # NOTE: original code had a broken requests.get with two URL args; fixed to proper single URL.
    r_topics = requests.get(
        f"https://winnersinstituteapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={batch_id}&subjectid={subject_id}",
        headers=hdr_auth,
    )
    topics = r_topics.json().get("data", [])
    if not topics:
        return await m.reply_text("Is subject me topics nahi mile.")

    ids_join = "&".join(str(t["topicid"]) for t in topics)
    details = []
    for t in topics:
        tid = t["topicid"]
        tname = t["topic_name"]
        details.append(f"```{tid}```  - **{tname}**")
    await m.reply_text("**TOPIC-ID  -  TOPIC**\n\n" + "\n".join(details))

    ask_topics = await m.reply_text(
        f"Ab **Topic IDs** bhejo `1&2&3` format me.\n\nFull subject ke liye:\n```{ids_join}```"
    )
    inp_topics = await client.listen(ask_topics.chat.id)
    topic_ids = [x.strip() for x in (inp_topics.text or "").split("&") if x.strip()]
    if not topic_ids:
        return await m.reply_text("Koi topic id nahi mili.")

    # resolution was never used; keep prompt for compatibility but ignore
    _ = await m.reply_text("**(Optional) Resolution bhejo — ignore kar sakte ho**")

    out_name = "WinnersInstitute.txt"
    # fresh file
    try:
        import os
        if os.path.exists(out_name):
            os.remove(out_name)
    except Exception:
        pass

    # ---- fetch classes for each topic & decode links ----
    for tid in topic_ids:
        r_classes = requests.get(
            f"https://winnersinstituteapi.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3?topicid={tid}&start=-1&courseid={batch_id}&subjectid={subject_id}",
            headers=hdr_auth,
        ).json()

        classes = r_classes.get("data", [])
        for item in classes:
            title = item.get("Title", "").strip()
            enc = item.get("download_link") or item.get("pdf_link") or ""
            if not enc:
                continue
            try:
                url = _aes_decode(enc)
            except Exception:
                # skip if decode fails
                continue

            with open(out_name, "a", encoding="utf-8") as f:
                f.write(f"{title}:{url}\n")

    await m.reply_document(out_name)
    await m.reply_text("✅ Done")
