# MIT License
# Code edited & cleaned by Cryptostark (Fixed Version)

import json
import requests
from pyromod import listen
from pyrogram import Client as bot, filters
from pyrogram.types import Message
import os
import time


@bot.on_message(filters.command("khan"))
async def khan_handler(bot, m: Message):

    editable = await m.reply_text(
        "Send **ID & Password** like this:\n\n`ID*Password`"
    )

    # USER INPUT
    input1: Message = await bot.listen(editable.chat.id)
    raw = input1.text

    if "*" not in raw:
        return await editable.edit("❌ Wrong format!\nUse: `ID*Password`")

    user = raw.split("*")[0]
    pwd = raw.split("*")[1]
    await input1.delete(True)

    # LOGIN API
    login_url = "https://api.penpencil.xyz/v1/oauth/token"

    headers = {
        'Host': 'api.penpencil.xyz',
        'authorization': 'Bearer c5c5e9c5721a1c4e322250fb31825b62f9715a4572318de90cfc93b02a8a8a75',
        'client-id': '5f439b64d553cc02d283e1b4',
        'client-version': '21.0',
        'user-agent': 'Android',
        'randomid': '385bc0ce778e8d0b',
        'client-type': 'MOBILE',
        'device-meta': '{APP_VERSION:19.0,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.khansirofficial}',
        'content-type': 'application/json; charset=UTF-8'
    }

    info = {
        "username": user,
        "password": pwd,
        "otp": "",
        "organizationId": "5f439b64d553cc02d283e1b4",
        "client_id": "system-admin",
        "client_secret": "KjPXuAVfC5xbmgreETNMaL7z",
        "grant_type": "password"
    }

    s = requests.Session()
    login = s.post(login_url, json=info, headers=headers)

    if login.status_code != 200:
        return await editable.edit("❌ Login failed! Check ID/Password")

    token = login.json()["data"]["access_token"]
    await editable.edit(f"✅ Login Successful\n\n`{token}`")

    # UPDATE HEADER AFTER LOGIN
    headers['authorization'] = f"Bearer {token}"

    # FETCH BATCHES
    params = {
        'mode': '1',
        'batchCategoryIds': '619bedc3394f824a71d8e721',
        'organisationId': '5f439b64d553cc02d283e1b4',
        'page': '1',
        'programId': '5f476e70a64b4a00ddd81379',
    }

    batches = s.get(
        'https://api.penpencil.xyz/v3/batches/my-batches',
        params=params,
        headers=headers
    ).json()["data"]

    cool = ""
    FFF = "**BATCH-ID — BATCH NAME**"

    for b in batches:
        line = f"```{b['_id']}``` — **{b['name']}**\n\n"
        if len(cool + line) > 4096:
            await editable.edit(cool)
            cool = ""
        cool += line

    await editable.edit(f"**Your Batches:**\n\n{FFF}\n\n{cool}")

    # GET BATCH ID
    ask = await m.reply_text("✅ **Send Batch ID:**")
    batch_id = (await bot.listen(ask.chat.id)).text

    # FETCH SUBJECTS
    details = s.get(
        f"https://api.penpencil.xyz/v3/batches/{batch_id}/details",
        headers=headers
    ).json()["data"]

    subjects = details["subjects"]
    batch_name = details["name"]

    subj_text = ""
    subj_ids = ""

    for sdata in subjects:
        subj_text += f"```{sdata['_id']}``` — **{sdata['name']}**\n"
        subj_ids += f"{sdata['_id']}&"

    msg2 = await m.reply_text(
        f"**Your Subjects:**\n\n{subj_text}\n\nSend Subject ID:\n```{subj_ids}```"
    )

    subject_id = (await bot.listen(msg2.chat.id)).text.strip()

    # FETCH TOPICS
    topics = s.get(
        f"https://api.penpencil.xyz/v2/batches/{batch_id}/subject/{subject_id}/topics?page=1",
        headers=headers
    ).json()["data"]

    topics_text = ""
    topic_ids = ""

    FF = "**TOPIC-ID — TOPIC — VIDEOS — PDF**"

    for t in topics:
        topics_text += f"```{t['_id']}``` — **{t['name']} — {t['videos']} — {t['notes']}**\n"
        topic_ids += f"{t['_id']}&"

    ask_topic = await m.reply_text(
        f"{FF}\n\n{topics_text}\n\nSend Topic IDs:\n```{topic_ids}```"
    )

    final_topics = (await bot.listen(ask_topic.chat.id)).text.split("&")

    # FINAL TXT FILE
    file_name = f"KhanSir-{batch_name}.txt"
    if os.path.exists(file_name):
        os.remove(file_name)

    # PROCESS ALL TOPICS
    for tid in final_topics:
        tid = tid.strip()
        if not tid:
            continue

        page1 = s.get(
            f"https://api.penpencil.xyz/v2/batches/{batch_id}/subject/{subject_id}/contents?page=1&tag={tid}&contentType=videos",
            headers=headers
        ).json()

        paginate = page1["paginate"]
        total_pages = paginate["totalCount"] // paginate["limit"] + 2

        for page in range(1, total_pages)[::-1]:
            data = s.get(
                f"https://api.penpencil.xyz/v2/batches/{batch_id}/subject/{subject_id}/contents?page={page}&tag={tid}&contentType=videos",
                headers=headers
            ).json()["data"]

            data.reverse()

            for vid in data:
                try:
                    title = vid["topic"]
                    url = vid["url"].replace(
                        "d1d34p8vz63oiq", "d3nzo6itypaz07"
                    ).replace("mpd", "m3u8")

                    with open(file_name, "a") as f:
                        f.write(f"{title}:{url}\n")

                except:
                    pass

    await m.reply_document(file_name)
    await m.reply_text("✅ Done")
