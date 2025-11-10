#  MIT License
#  (header unchanged)

import json
import os
import re
import time
import requests
import cloudscraper

from pyrogram import Client, filters
from pyrogram.types import Message

# NOTE:
# - ~filters.edited HATA DIYA
# - imports cleaned
# - output file ka naam batch name (bn) par fix, taaki undefined t_name issue na aaye
# - small safety around JSON parsing

ACCOUNT_ID = "6206459123001"
BCOV_POLICY = (
    "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd"
)
BC_URL = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos"
BC_HDR = {"BCOV-POLICY": BCOV_POLICY}


@Client.on_message(filters.command(["cw"]))
async def account_login(bot: Client, m: Message):
    s = requests.Session()

    login_url = "https://elearn.crwilladmin.com/api/v1/login-other"
    data = {
        "deviceType": "android",
        "password": "",
        "deviceIMEI": "08750aa91d7387ab",
        "deviceModel": "Realme RMX2001",
        "deviceVersion": "R(Android 11.0)",
        "email": "",
        "deviceToken": "fYdfgaUaQZmYP7vV4r2rjr:APA91bFPn3Z4m_YS8kYQSthrueUh-lyfxLghL9ka-MT0m_4TRtlUu7cy90L8H6VbtWorg95Car6aU9zjA-59bZypta9GNNuAdUxTnIiGFxMCr2G3P4Gf054Kdgwje44XWzS9ZGa4iPZh",
    }
    headers = {
        "Host": "elearn.crwilladmin.com",
        "Token": "",
        "Usertype": "",
        "Appver": "1.55",
        "Apptype": "android",
        "Content-Type": "application/json; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate",
        "user-agent": "okhttp/5.0.0-alpha.2",
        "Connection": "Keep-Alive",
    }

    editable = await m.reply_text(
        "Send **ID & Password** like `ID*Password`\n\nOR send **TOKEN** only."
    )
    inp: Message = await bot.listen(editable.chat.id)
    raw_text = inp.text.strip()

    # Get token
    if "*" in raw_text:
        data["email"] = raw_text.split("*")[0]
        data["password"] = raw_text.split("*")[1]
        try:
            r = s.post(login_url, headers=headers, json=data, timeout=15)
            r.raise_for_status()
            token = r.json()["data"]["token"]
        except Exception:
            await m.reply_text("Login failed.")
            return
    else:
        token = raw_text

    # My batches
    try:
        j = s.get(
            f"https://elearn.crwilladmin.com/api/v1/comp/my-batch?&token={token}",
            timeout=20,
        ).json()
        batches = j["data"]["batchData"]
    except Exception:
        await m.reply_text("Failed to fetch batches.")
        return

    cool = ""
    FFF = "**BATCH-ID - BATCH NAME - INSTRUCTOR**"
    for b in batches:
        aa = f" ```{b['id']}```  - **{b['batchName']}**\n{b.get('instructorName','')}\n\n"
        if len(f"{cool}{aa}") > 4096:
            await m.reply_text(cool)
            cool = ""
        cool += aa
    await editable.edit(f"**You have these batches :-**\n\n{FFF}\n\n{cool}")

    editable1 = await m.reply_text("**Now send the Batch ID to Download**")
    inp2: Message = await bot.listen(editable.chat.id)
    batch_id = inp2.text.strip()

    # Topics for the batch
    try:
        j2 = s.get(
            f"https://elearn.crwilladmin.com/api/v1/comp/batch-topic/{batch_id}?type=class&token={token}",
            timeout=20,
        ).json()
        topics = j2["data"]["batch_topic"]
        bn = j2["data"]["batch_detail"]["name"]
    except Exception:
        await m.reply_text("Failed to fetch topics.")
        return

    vj = ""
    cool1 = ""
    BBB = "**TOPIC-ID - TOPIC - VIDEOS**"
    for t in topics:
        tid = str(t["id"])
        tname = t["topicName"].replace(" ", "")
        # fetch class count for display
        try:
            det = s.get(
                f"https://elearn.crwilladmin.com/api/v1/comp/batch-detail/{batch_id}?redirectBy=mybatch&topicId={tid}&token={token}",
                timeout=20,
            ).json()
            classes = list(reversed(det["data"]["class_list"]["classes"]))
            zz = len(classes)
        except Exception:
            zz = 0

        vj += f"{tid}&"
        line = f"```{tid}```     - **{tname} - ({zz})**\n"
        if len(f"{cool1}{line}") > 4096:
            await m.reply_text(cool1)
            cool1 = ""
        cool1 += line

    await m.reply_text(f'Batch details of **{bn}** are:\n\n{BBB}\n\n{cool1}')
    editable2 = await m.reply_text(
        "Now send the **Topic IDs** to Download\n\n"
        "Send like `1&2&3&4` etc.\n\n"
        f"**Enter this to download full batch :-**\n```{vj}```"
    )
    inp3: Message = await bot.listen(editable.chat.id)
    raw_topics = inp3.text.strip()

    # Output file per batch
    mm = "CareerWill"
    out_file = f"{mm} - {bn}.txt"

    try:
        xv = [x for x in raw_topics.split("&") if x.strip()]
        for t in xv:
            # Batch detail per topic
            r = s.get(
                f"https://elearn.crwilladmin.com/api/v1/comp/batch-detail/{batch_id}"
                f"?redirectBy=mybatch&topicId={t}&token={token}",
                timeout=30,
            )
            ff = r.json()
            classes = list(reversed(ff["data"]["class_list"]["classes"]))

            for cls in classes:
                vidid = str(cls["id"])
                lesson_name = cls.get("lessonName", "").replace("/", "_").strip()
                if not lesson_name:
                    lesson_name = vidid

                sources = cls.get("lessonUrl", [])
                bcvid = sources[0]["link"] if sources else ""

                link = ""
                try:
                    if bcvid.startswith("62") or bcvid.startswith("63"):
                        # Brightcove
                        vj = s.get(f"{BC_URL}/{bcvid}", headers=BC_HDR, timeout=20).json()
                        # pick one of the sources (index 5 was used in old code)
                        srcs = vj.get("sources", [])
                        if not srcs:
                            raise ValueError("No sources in BC response")
                        pick = srcs[min(5, len(srcs) - 1)]
                        video_url = pick["src"]

                        tok = s.get(
                            f"https://elearn.crwilladmin.com/api/v1/livestreamToken"
                            f"?type=brightcove&vid={vidid}&token={token}",
                            timeout=15,
                        ).json()["data"]["token"]
                        link = f"{video_url}&bcov_auth={tok}"
                    else:
                        # YouTube embed fallback
                        link = f"https://www.youtube.com/embed/{bcvid}" if bcvid else ""
                except Exception:
                    # safest fallback
                    link = f"https://www.youtube.com/embed/{bcvid}" if bcvid else ""

                with open(out_file, "a", encoding="utf-8") as f:
                    f.write(f"{lesson_name}:{link}\n")

        await m.reply_document(out_file)
    except Exception as e:
        await m.reply_text(str(e))
    finally:
        try:
            if os.path.isfile(out_file):
                os.remove(out_file)
        except Exception:
            pass

    # Notes (optional)
    try:
        ask = await m.reply_text("Do you want download notes? Send **y** or **n**")
        inp5: Message = await bot.listen(editable.chat.id)
        if inp5.text.strip().lower() == "y":
            scraper = cloudscraper.create_scraper()
            rpdf = scraper.get(
                f"https://elearn.crwilladmin.com/api/v1/comp/batch-notes/{batch_id}"
                f"?topicid={batch_id}&token={token}",
                timeout=30,
            )
            pdfD = rpdf.json()
            notes = list(reversed(pdfD["data"]["notesDetails"]))
            note_file = f"{mm} - {bn} - notes.txt"
            for doc in notes:
                name = doc.get("docTitle", "note")
                url = doc.get("docUrl", "")
                with open(note_file, "a", encoding="utf-8") as f:
                    f.write(f"{name}:{url}\n")
            await m.reply_document(note_file)
            try:
                os.remove(note_file)
            except Exception:
                pass
    except Exception:
        pass

    await m.reply_text("Done")
