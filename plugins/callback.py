#!/usr/bin/env python3
# Copyright (C) @subinps
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from pyrogram.types import InputMediaVideo
from pyrogram.errors import FloodWait, MessageIdInvalid
import time
from utils import VIDEO_DICT, TG_SUCKS, FIX_TG_SUCKS, get_height_and_width, get_link, trim_video, get_time_hh_mm_ss, short_num, progress_bar
import os
from yt_dlp import YoutubeDL
from config import Config


BOT = {} # to store bot username for avoiding floodwait.

@Client.on_callback_query(filters.regex(r"^trim"))
async def cb_handler(client: Client, query: CallbackQuery):
    _, start, end, vid, user = query.data.split(":")
    BLAME_TG = False
    if query.from_user.id != int(user):
        return await query.answer("Okda", show_alert=True)
    begin = time.time()
    try:
        await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption="Getting Video Details..")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption="Getting Video Details..")
    except MessageIdInvalid:
        # Telegram fails to edit inline media for some unknown reason.
        if not BOT.get("me"):
            BOT["me"] = (await client.get_me()).username
        user_name = BOT['me']
        await query.answer(url=f"https://t.me/{user_name}?start=tgsucks_{vid}_{start}_{end}")
        BLAME_TG = True
    except Exception as e:
        print(e)
    await query.answer("Please Wait...")
    info = VIDEO_DICT.get(vid) # Once fetched , info are saved to a dict for faster query in future .
    if info:
        dur = info['dur']
        view = info['views']
        title = info['title']
        id = vid
    else:
        try:
            ydl_opts = {
                "quite": True,
                "geo-bypass": True,
                "nocheckcertificate": True
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(vid, download=False)                
        except:
            info = None
        dur = get_time_hh_mm_ss(info["duration"])
        view = short_num(info["view_count"])
        id = info['id']
        title = info['title']
        VIDEO_DICT[id] = {'dur':dur, 'views':view, 'title':title}

    tdur  = int(end) - int(start)

    if info:
        caption = f"<a href=https://www.youtube.com/watch?v={id}&t={start}>{title}</a>\n👀 Views: {view}\n🎞 Duration: {dur}\n✂️ Trim Duration: {tdur} seconds (from `{get_time_hh_mm_ss(start)}` to `{get_time_hh_mm_ss(end)}`)"
    else:
        caption = f"<a href=https://www.youtube.com/watch?v={id}&t={start}>{title}</a>\n✂️ Trim Duration: {tdur} (from {get_time_hh_mm_ss(start)} to {get_time_hh_mm_ss(end)})"
    
    link = await get_link(vid) # generate a direct download link for video 
    try:
        await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption=caption + "\n\nStatus: Getting Video Details..")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption=caption + "\n\nStatus: Getting Video Details..")
    except MessageIdInvalid:
        BLAME_TG = True
    except Exception as e:
        print(e)
    if not link:
        return await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption="❌ Failed to generate sufficient info.")
    out = f"{query.inline_message_id}.mp4"
    thumb = f"{query.inline_message_id}.jpeg"
    try:
        await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption=caption + "\n\nStatus: Trimming Your Video...")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption=caption + "\n\nStatus: Trimming Your Video...")
    except MessageIdInvalid:
        BLAME_TG = True
    except Exception as e:
        print(e)
    await trim_video(link, start, end, out, thumb)
    if (not os.path.exists(out)) or (
        os.path.getsize(out) == 0
        ):
        return await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption="❌ Failed")
    if (not os.path.exists(thumb)) or (
        os.path.getsize(thumb) == 0
        ):
        thumb = None
    p_end = time.time()
    try:
        await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption=caption + "\n\nStatus:Uploading Your Video To Telegram.")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption=caption + "\n\nStatus:Uploading Your Video To Telegram.")
    except MessageIdInvalid:
        BLAME_TG = True
    except Exception as e:
        print(e)
    width, height = await get_height_and_width(out)
    upload = await client.send_video(
        Config.LOG_CHANNEL, 
        out, 
        caption, 
        duration=tdur,
        supports_streaming=True,
        thumb = thumb, 
        width = width, 
        height = height,
        progress=progress_bar,
        progress_args=(client, time.time(), query.inline_message_id, caption)
    )
    media = InputMediaVideo(upload.video.file_id, caption=caption+ f"\nStatus: Succesfully Uploaded.\nTime Taken {round(p_end-begin)} Seconds")
    try:
        await client.edit_inline_media(query.inline_message_id, media)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await client.edit_inline_media(query.inline_message_id, media)
    except MessageIdInvalid:
        BLAME_TG = True
    except Exception as e:
        print(e)
    if BLAME_TG:
        if FIX_TG_SUCKS.get(f'{vid}_{start}_{end}'):
            await client.send_video(query.from_user.id, upload.video.file_id, caption=caption+ f"\nStatus: Succesfully Uploaded.\nTime Taken {round(p_end-begin)} Seconds")
        TG_SUCKS[f'{vid}_{start}_{end}'] = {'file_id':upload.video.file_id, 'caption':caption+ f"\nStatus: Succesfully Uploaded.\nTime Taken {round(p_end-begin)} Seconds"}
    try:
        os.remove(out)
        os.remove(thumb)
    except:
        pass


