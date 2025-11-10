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
import time
import os

@bot.on_message(filters.command(["pw"]))
async def account_login(bot: Client, m: Message):

    editable = await m.reply_text(
        "Send **Auth code** in this manner otherwise bot will not respond.\n\nSend like this:-  **AUTH CODE**"
    )

    input1: Message = await bot.listen(editable.chat.id)
    raw_text1 = input1.text
    await input1.delete()

    headers = {
        'Host': 'api.penpencil.xyz',
        'authorization': f"Bearer {raw_text1}",
        'client-id': '5eb393ee95fab7468a79d189',
        'client-version': '12.84',
        'user-agent': 'Android',
        'randomid': 'e4307177362e86f1',
        'client-type': 'MOBILE',
        'device-meta': '{APP_VERSION:12.84,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.physicswalb}',
        'content-type': 'application/json; charset=UTF-8',
    }

    params = {
        'mode': '1',
        'filter': 'false',
        'exam': '',
        'amount': '',
        'organisationId': '5eb393ee95fab7468a79d189',
        'classes': '',
        'limit': '20',
        'page': '1',
        'programId': '',
        'ut': '1652675230446',
    }

    await editable.edit("**You have these Batches :-\n\nBatch ID : Batch Name**")

    response = requests.get(
        'https://api.penpencil.xyz/v3/batches/my-batches',
        params=params,
        headers=headers
    ).json()["data"]

    # FIX: batch variable needed outside loop
    batch_names = {}

    for data in response:
        batch_name = data["name"]
        batch_id = data["_id"]
        batch_names[batch_id] = batch_name
        aa = f"```{batch_name}```  :  ```{batch_id}```"
        await m.reply_text(aa)

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    input3 = await bot.listen(editable1.chat.id)
    raw_text3 = input3.text
    await input3.delete()

    if raw_text3 not in batch_names:
        await editable1.edit("❌ Invalid Batch ID")
        return

    batch = batch_names[raw_text3]

    response2 = requests.get(
        f'https://api.penpencil.xyz/v3/batches/{raw_text3}/details',
        headers=headers
    ).json()["data"]["subjects"]

    await editable1.edit("subject : subjectId")

    vj = ""
    for data in response2:
        bb = f"{data['_id']}&"
        await m.reply_text(bb)

    for data in response2:
        tids = data['_id']
        idid = f"{tids}&"
        if len(vj + idid) > 4096:
            await m.reply_text(idid)
            vj = ""
        vj += idid

    editable2 = await m.reply_text(f"**Enter this to download full batch :-**\n```{vj}```")

    input4 = await bot.listen(editable2.chat.id)
    raw_text4 = input4.text
    await input4.delete()

    await m.reply_text("**Enter resolution**")
    input5: Message = await bot.listen(editable2.chat.id)
    raw_text5 = input5.text
    await input5.delete()

    editable4 = await m.reply_text(
        "Now send the **Thumb url** Eg : ```https://telegra.ph/file/d9e24878bd4aba05049a1.jpg```\n\nor Send **no**"
    )
    input6 = await bot.listen(editable4.chat.id)
    raw_text6 = input6.text
    thumb = raw_text6

    if thumb.startswith("http://") or thumb.startswith("https://"):
        subprocess.getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    try:
        xv = raw_text4.split('&')

        # FIX: Clear file before writing
        if os.path.exists(f"{batch}.txt"):
            os.remove(f"{batch}.txt")

        for t in xv:
            t = t.strip()
            if not t:
                continue

            params1 = {'page': '1', 'tag': '', 'contentType': 'exercises-notes-videos', 'ut': ''}
            params2 = {'page': '2', 'tag': '', 'contentType': 'exercises-notes-videos', 'ut': ''}
            params3 = {'page': '3', 'tag': '', 'contentType': 'exercises-notes-videos', 'ut': ''}
            params4 = {'page': '4', 'tag': '', 'contentType': 'exercises-notes-videos', 'ut': ''}

            pages = [
                requests.get(f'https://api.penpencil.xyz/v2/batches/{raw_text3}/subject/{t}/contents',
                              params=params1, headers=headers).json()["data"],
                requests.get(f'https://api.penpencil.xyz/v2/batches/{raw_text3}/subject/{t}/contents',
                              params=params2, headers=headers).json()["data"],
                requests.get(f'https://api.penpencil.xyz/v2/batches/{raw_text3}/subject/{t}/contents',
                              params=params3, headers=headers).json()["data"],
                requests.get(f'https://api.penpencil.xyz/v2/batches/{raw_text3}/subject/{t}/contents',
                              params=params4, headers=headers).json()["data"]
            ]

            for resp in pages:
                try:
                    for data in resp:
                        title = data["topic"]
                        url = data["url"].replace(
                            "d1d34p8vz63oiq", "d3nzo6itypaz07"
                        ).replace("mpd", "m3u8").strip()

                        with open(f"{batch}.txt", "a") as f:
                            f.write(f"{title}:{url}\n")

                except Exception as e:
                    await m.reply_text(str(e))

        await m.reply_document(f"{batch}.txt")

    except Exception as e:
        await m.reply_text(str(e))
