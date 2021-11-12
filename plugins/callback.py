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
import time
from utils import VIDEO_DICT, get_height_and_width, get_link, trim_video, get_time_hh_mm_ss, short_num, progress_bar
import os
from yt_dlp import YoutubeDL
from config import Config

@Client.on_callback_query(filters.regex(r"^trim"))
async def cb_handler(client: Client, query: CallbackQuery):
    _, start, end, vid, user = query.data.split(":")
    if query.from_user.id != int(user):
        return await query.answer("Okda", show_alert=True)
    begin = time.time()
    await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption="Getting Video Details..")
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
        caption = f"<a href=https://www.youtube.com/watch?v={id}>{title}</a>\n👀 Views: {view}\n🎞 Duration: {dur}\n✂️ Trim Duration: {tdur} seconds (from `{get_time_hh_mm_ss(start)}` to `{get_time_hh_mm_ss(end)}`)"
    else:
        caption = f"<a href=https://www.youtube.com/watch?v={id}>{title}</a>\n✂️ Trim Duration: {tdur} (from {get_time_hh_mm_ss(start)} to {get_time_hh_mm_ss(end)})"
    
    link = await get_link(vid) # generate a direct download link for video 
    await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption=caption + "\n\nStatus: Getting Video Details..")
    if not link:
        return await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption="❌ Failed to generate sufficient info.")
    out = f"{query.inline_message_id}.mp4"
    thumb = f"{query.inline_message_id}.jpeg"
    await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption=caption + "\n\nStatus: Trimming Your Video...")
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
    await client.edit_inline_caption(inline_message_id = query.inline_message_id, caption=caption + "\n\nStatus:Uploading Your Video To Telegram.")
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
    await client.edit_inline_media(query.inline_message_id, media)
    try:
        os.remove(out)
        os.remove(thumb)
    except:
        pass


