#  MIT License
#  Copyright (c) 2019-present Dan
#  Code edited & cleaned

import json
import os
import requests

from pyrogram import Client, filters
from pyrogram.types import Message

# NOTE: pyromod.listen enable karta hai .listen() ko
try:
    from pyromod import listen  # noqa: F401
except Exception:
    pass


def _chunk_text(s: str, limit: int = 4000):
    """Telegram message size handle karne ke liye chhote parts me split."""
    for i in range(0, len(s), limit):
        yield s[i : i + limit]


@Client.on_message(filters.command(["cp"]))  # << ~filters.edited HATA DIYA
async def account_login(bot: Client, m: Message):
    s = requests.Session()

    # 1) Token manga lo
    prompt = await m.reply_text("**ClassPlus Token bhejo**\n\n`x-access-token` value paste karo:")
    token_msg: Message = await bot.listen(m.chat.id)
    token = token_msg.text.strip()
    await token_msg.delete(True)

    headers = {
        "authority": "api.classplusapp.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en",
        "api-version": "28",
        "cache-control": "no-cache",
        "device-id": "516",
        "origin": "https://web.classplusapp.com",
        "pragma": "no-cache",
        "referer": "https://web.classplusapp.com/",
        "region": "IN",
        "sec-ch-ua": '"Chromium";v="107", "Not=A?Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "x-access-token": token,
    }

    await prompt.edit("**Login verify kar raha hu...**")
    r = s.get(
        "https://api.classplusapp.com/v2/batches/details?limit=20&offset=0&sortBy=createdAt",
        headers=headers,
        timeout=15,
    )

    if r.status_code != 200:
        return await m.reply_text(
            f"❌ **Login Failed**\nHTTP {r.status_code}\nResponse: `{r.text[:500]}`"
        )

    try:
        batches = r.json()["data"]["totalBatches"]
    except Exception as e:
        return await m.reply_text(f"❌ Unexpected response format: `{e}`\n`{r.text[:1000]}`")

    # 2) Batches dikhado
    title = "**You have these batches :-**\n\n**BATCH-ID - BATCH NAME**\n\n"
    body = ""
    for b in batches:
        body += f"```{b['batchId']}```  - **{b['batchName']}**\n\n"

    for chunk in _chunk_text(title + body):
        await m.reply_text(chunk)

    # 3) Course ID lo
    ask_course = await m.reply_text("**Ab Course/Batch ID bhejo** (jo upar dikh raha hai):")
    course_msg: Message = await bot.listen(m.chat.id)
    course_id = course_msg.text.strip()
    await course_msg.delete(True)
    await ask_course.delete(True)

    # 4) Course content (top-level folders)
    rr = s.get(
        f"https://api.classplusapp.com/v2/course/content/get?courseId={course_id}",
        headers=headers,
        timeout=15,
    )
    if rr.status_code != 200:
        return await m.reply_text(
            f"❌ Content fetch failed (course level)\nHTTP {rr.status_code}"
        )

    try:
        top_content = rr.json()["data"]["courseContent"]
    except Exception as e:
        return await m.reply_text(f"❌ Parse error: `{e}`\n`{rr.text[:1000]}`")

    title = "**You have these Folders :-**\n\n**FOLDER-ID - FOLDER NAME**\n\n"
    body = ""
    for item in top_content:
        body += f"```{item['id']}```  - **{item.get('name','-')}**\n\n"

    for chunk in _chunk_text(title + body):
        await m.reply_text(chunk)

    # 5) Folder ID lo (first level)
    ask_folder = await m.reply_text("**Folder ID bhejo** (first level):")
    folder_msg: Message = await bot.listen(m.chat.id)
    folder_id_lvl1 = folder_msg.text.strip()
    await folder_msg.delete(True)
    await ask_folder.delete(True)

    rr2 = s.get(
        f"https://api.classplusapp.com/v2/course/content/get?courseId={course_id}&folderId={folder_id_lvl1}",
        headers=headers,
        timeout=15,
    )
    if rr2.status_code != 200:
        return await m.reply_text(
            f"❌ Content fetch failed (folder level)\nHTTP {rr2.status_code}"
        )

    try:
        folder_content_lvl1 = rr2.json()["data"]["courseContent"]
    except Exception as e:
        return await m.reply_text(f"❌ Parse error: `{e}`\n`{rr2.text[:1000]}`")

    # Show folders/files summary
    title = (
        "**You have these Folders :-**\n\n"
        "**FOLDER-ID - FOLDER NAME - TOTAL VIDEOS - TOTAL FILES**\n\n"
    )
    body = ""
    for item in folder_content_lvl1:
        body += (
            f"```{item['id']}``` - **{item.get('name','-')}  "
            f"- {item.get('resources',{}).get('videos',0)}  "
            f"- {item.get('resources',{}).get('files',0)}**\n\n"
        )
    for chunk in _chunk_text(title + body):
        await m.reply_text(chunk)

    # Kya ye nested folder hai?
    is_nested = False
    if folder_content_lvl1 and isinstance(folder_content_lvl1[0], dict):
        is_nested = folder_content_lvl1[0].get("contentType") == 1

    download_list_file = "classplus.txt"
    if os.path.exists(download_list_file):
        try:
            os.remove(download_list_file)
        except Exception:
            pass

    if is_nested:
        # 6) Second level folder ID
        ask_folder2 = await m.reply_text("**Ye nested Folder lag raha hai. Second-level Folder ID bhejo:**")
        folder2_msg: Message = await bot.listen(m.chat.id)
        folder_id_lvl2 = folder2_msg.text.strip()
        await folder2_msg.delete(True)
        await ask_folder2.delete(True)

        rr3 = s.get(
            f"https://api.classplusapp.com/v2/course/content/get?courseId={course_id}&folderId={folder_id_lvl2}",
            headers=headers,
            timeout=15,
        )
        if rr3.status_code != 200:
            return await m.reply_text(
                f"❌ Content fetch failed (second level)\nHTTP {rr3.status_code}"
            )

        try:
            leaf_items = rr3.json()["data"]["courseContent"]
        except Exception as e:
            return await m.reply_text(f"❌ Parse error: `{e}`\n`{rr3.text[:1000]}`")

        leaf_items.reverse()
        title = "**You have these Videos :-**\n\n**TOPIC-ID - TOPIC NAME**\n\n"
        body = ""

        with open(download_list_file, "a", encoding="utf-8") as f:
            for it in leaf_items:
                it_id = it.get("id")
                nm = it.get("name", "-")
                desc = it.get("description", "").strip()
                url = it.get("url", "").strip()

                body += f"```{it_id}``` - **{nm} - {desc}**\n\n"
                if url:
                    f.write(f"{nm}-{desc}:{url}\n")

        for chunk in _chunk_text(title + body):
            await m.reply_text(chunk)

    else:
        # Direct leaf (videos/files in this folder)
        folder_content_lvl1.reverse()
        title = "**You have these Videos :-**\n\n**TOPIC-ID - TOPIC NAME**\n\n"
        body = ""

        with open(download_list_file, "a", encoding="utf-8") as f:
            for it in folder_content_lvl1:
                it_id = it.get("id")
                nm = it.get("name", "-")
                desc = it.get("description", "").strip()
                url = it.get("url", "").strip()

                body += f"```{it_id}``` - **{nm} - {desc}**\n\n"
                if url:
                    f.write(f"{nm}-{desc}:{url}\n")

        for chunk in _chunk_text(title + body):
            await m.reply_text(chunk)

    # 7) TXT bhej do
    try:
        await m.reply_document(download_list_file)
    except Exception as e:
        await m.reply_text(f"TXT bhejte waqt error: `{e}`")
    finally:
        try:
            os.remove(download_list_file)
        except Exception:
            pass
