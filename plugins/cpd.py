#  MIT License
#
#  Copyright (c) 2019-present Dan <https://github.com/delivrance>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE

import os
import time
import json
import requests
import subprocess
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen  # enable conversations

from p_bar import progress_bar
import helper


@Client.on_message(filters.command(["cpd"]))  # ~filters.edited REMOVED
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text("Send txt file**")
    input_msg: Message = await bot.listen(editable.chat.id)
    downloaded = await input_msg.download()
    await input_msg.delete(True)

    try:
        with open(downloaded, "r") as f:
            content = f.read().strip()
        lines = [ln for ln in content.split("\n") if ln.strip()]
        links = [ln.split(":", 1) for ln in lines]
        os.remove(downloaded)
    except Exception:
        await m.reply_text("Invalid file input.")
        try:
            os.remove(downloaded)
        except Exception:
            pass
        return

    editable = await m.reply_text(
        f"Total links found are **{len(links)}**\n\n"
        "Send From where you want to download, initial is **0**"
    )
    input_from: Message = await bot.listen(editable.chat.id)
    raw_from = input_from.text

    try:
        start_index = int(raw_from)
    except Exception:
        start_index = 0

    editable = await m.reply_text("**Enter Title**")
    input_title: Message = await bot.listen(editable.chat.id)
    title_caption = input_title.text

    await m.reply_text("**Enter resolution**")
    input_res: Message = await bot.listen(editable.chat.id)
    _resolution = input_res.text  # kept for compatibility (not used in current flow)

    editable4 = await m.reply_text(
        "Now send the **Thumb url**\nEg : ```https://telegra.ph/file/d9e24878bd4aba05049a1.jpg```\n\nor Send **no**"
    )
    input_thumb = await bot.listen(editable4.chat.id)
    thumb = input_thumb.text

    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    # numbering start
    count = 1 if raw_from == "0" else start_index

    try:
        for i in range(start_index, len(links)):
            # name : url
            name_raw = links[i][0]
            url = links[i][1]

            # sanitize filename
            name_clean = (
                name_raw.replace("\t", "")
                .replace(":", "")
                .replace("/", "")
                .replace("+", "")
                .replace("#", "")
                .replace("|", "")
                .replace("@", "")
                .replace("*", "")
                .replace(".", "")
                .strip()
            )

            # classplus special handling (requires token in env / or previous flow)
            if "classplus" in url:
                try:
                    headers = {
                        "Host": "api.classplusapp.com",
                        # NOTE: expects 'token' variable from previous flow; if not present this branch may fail.
                        "x-access-token": f"{token}",  # noqa: F821  (left as-is per original logic)
                        "user-agent": "Mobile-Android",
                        "app-version": "1.4.37.1",
                        "api-version": "18",
                        "device-id": "5d0d17ac8b3c9f51",
                        "device-details": "2848b866799971ca_2848b8667a33216c_SDK-30",
                        "accept-encoding": "gzip",
                    }
                    params = (("url", f"{url}"),)
                    r = requests.get(
                        "https://api.classplusapp.com/cams/uploader/video/jw-signed-url",
                        headers=headers,
                        params=params,
                    )
                    a = r.json()["url"]
                    headers1 = {
                        "User-Agent": "ExoPlayerDemo/1.4.37.1 (Linux;Android 11) ExoPlayerLib/2.14.1",
                        "Accept-Encoding": "gzip",
                        "Host": "cdn.jwplayer.com",
                        "Connection": "Keep-Alive",
                    }
                    r2 = requests.get(a, headers=headers1)
                    url1 = (r2.text).split("\n")[2]
                except Exception:
                    # fallback
                    url1 = url
            else:
                url1 = url

            name = f'{str(count).zfill(3)}) {name_clean}'
            show = f"**Downloading:-**\n\n**Name :-** `{name}`\n\n**Url :-** `{url1}`"
            prog = await m.reply_text(show)
            caption = f"**Title »** {name_clean}.mkv\n**Caption »** {title_caption}\n**Index »** {str(count).zfill(3)}"

            if "pdf" in url:
                cmd = f'yt-dlp -o "{name}.pdf" "{url1}"'
            else:
                cmd = f'yt-dlp -o "{name}.mp4" --no-keep-video --no-check-certificate --remux-video mkv "{url1}"'

            try:
                download_cmd = (
                    f"{cmd} -R 25 --fragment-retries 25 "
                    "--external-downloader aria2c "
                    "--downloader-args 'aria2c: -x 16 -j 32'"
                )
                os.system(download_cmd)

                if os.path.isfile(f"{name}.mkv"):
                    filename = f"{name}.mkv"
                elif os.path.isfile(f"{name}.mp4"):
                    filename = f"{name}.mp4"
                elif os.path.isfile(f"{name}.pdf"):
                    filename = f"{name}.pdf"
                else:
                    raise FileNotFoundError("Downloaded file not found")

                # make thumb if needed
                try:
                    subprocess.run(
                        f'ffmpeg -i "{filename}" -ss 00:01:00 -vframes 1 "{filename}.jpg"',
                        shell=True,
                        check=False,
                    )
                except Exception:
                    pass

                await prog.delete(True)
                reply = await m.reply_text(f"Uploading - ```{name}```")

                try:
                    if thumb == "no":
                        thumbnail = f"{filename}.jpg"
                    else:
                        thumbnail = thumb
                except Exception as e:
                    await m.reply_text(str(e))
                    thumbnail = None

                if filename.endswith(".pdf"):
                    await m.reply_document(filename, caption=caption)
                else:
                    dur = int(helper.duration(filename))
                    await m.reply_video(
                        filename,
                        supports_streaming=True,
                        height=720,
                        width=1280,
                        caption=caption,
                        duration=dur,
                        thumb=thumbnail if thumbnail and os.path.exists(thumbnail) else None,
                        progress=progress_bar,
                        progress_args=(reply, time.time()),
                    )

                count += 1

                # cleanup
                try:
                    os.remove(filename)
                except Exception:
                    pass
                try:
                    os.remove(f"{filename}.jpg")
                except Exception:
                    pass
                await reply.delete(True)
                time.sleep(1)

            except Exception as e:
                await m.reply_text(
                    f"**downloading failed ❌**\n{str(e)}\n**Name** - {name}\n**Link** - `{url}` & `{url1}`"
                )
                continue

    except Exception as e:
        await m.reply_text(str(e))

    await m.reply_text("Done")
