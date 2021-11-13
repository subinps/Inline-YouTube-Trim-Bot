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

from pyrogram.handlers import InlineQueryHandler
from youtubesearchpython import VideosSearch
from pyrogram.types import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    InlineQueryResultPhoto,
    InlineQueryResultArticle, 
    InputTextMessageContent
    )
from pyrogram import (
    Client, 
    errors
)
import re
from utils import get_time, get_time_hh_mm_ss, short_num, VIDEO_DICT, get_buttons
from yt_dlp import YoutubeDL


@Client.on_inline_query()
async def search(client, query):
    answers = []
    user = query.from_user.id
    string = query.query.strip().rstrip()
    keyword = string
    start, end = None, None
    if '|' in string:
        times = string.split("|", 1)
    elif '?t=' in string:
        times = string.split("?t=", 1)
    elif '&t=' in string:
        times = string.split("&t=", 1)
    else:
        times = []
    if len(times) == 2:
        keyword = (times[0]).strip()
        try:
            start_, end_ = (times[1]).strip().split(None, 1)
            start = get_time(start_.strip())
            end = get_time(end_.strip())
        except:
            start, end = None, None
    if string == "":
        answers.append(
            InlineQueryResultArticle(
                title="Usage Guide",
                description=("How to use me?!"),
                input_message_content=InputTextMessageContent("Just type Bot username followed by a space and your youtube query and use | or '&t=' or '?t=' to specify trim duration and make sure to seperate start and end points with a space.\n\nExample: `@TrimYtbot Niram | 1:25:1 1:26:6` or `@TrimYtbot Niram | 1800 2000`\n\n__Note: You can specify timestamps either in Hour:Minute:Seconds or Minute:Seconds format or in seconds.__"),
                reply_markup=InlineKeyboardMarkup(get_buttons(start, end, get_time(0), "start", user, ""))
                )
            )
        return await query.answer(results=answers, cache_time=0)
    
    else:
        regex = r"^(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?"
        match = re.match(regex, keyword)
        if match:
            if not VIDEO_DICT.get(match.group(1)):
                try:
                    ydl_opts = {
                        "quite": True,
                        "geo-bypass": True,
                        "nocheckcertificate": True
                    }
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(keyword, download=False)                
                except:
                    return await query.answer(
                        results=answers,
                        cache_time=0,
                        switch_pm_text=("Nothing found"),
                        switch_pm_parameter="help",
                    )
                if not info:
                    return await query.answer(
                        results=answers,
                        cache_time=0,
                        switch_pm_text=("Nothing found"),
                        switch_pm_parameter="help",
                    )
                dur = get_time_hh_mm_ss(info["duration"])
                view = f'{short_num(info["view_count"])} views'
                id = info['id']
                title = info['title']
                VIDEO_DICT[id] = {'dur':dur, 'views':view, 'title':title}
            else:
                info = VIDEO_DICT.get(match.group(1))
                dur = info['dur']
                view = info['views']
                title = info['title']
                id  = match.group(1)
            buttons = get_buttons(start, end, get_time(dur), id, user, keyword)
            caption = f"<a href=https://www.youtube.com/watch?v={id}>{title}</a>\n👀 Views: {view}\n🎞 Duration: {dur}"
            if start and end:
                caption += f"\n✂️ Selected Trim Duration: {get_time_hh_mm_ss(start)} to {get_time_hh_mm_ss(end)}"
            if len(buttons) == 1:
                caption += "\n😬 No Valid Trim Duration Specified."
            answers.append(
                InlineQueryResultPhoto(
                    photo_url=f'https://i.ytimg.com/vi/{id}/hqdefault.jpg',
                    title=title,
                    description=("Duration: {} Views: {}").format(
                        dur,
                        view
                    ),
                    caption=caption,
                    thumb_url=f'https://i.ytimg.com/vi/{id}/hqdefault.jpg',
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            )
        else:
            videosSearch = VideosSearch(keyword.lower(), limit=50)
            for v in videosSearch.result()["result"]:
                buttons = get_buttons(start, end, get_time(v["duration"]),  v['id'], user, keyword)
                caption = f"<a href=https://www.youtube.com/watch?v={v['id']}>{v['title']}</a>\n👀 Views: {v['viewCount']['short']}\n🎞 Duration: {v['duration']}"
                if start and end:
                    caption += f"\n✂️ Selected Trim Duration: {get_time_hh_mm_ss(start)} to {get_time_hh_mm_ss(end)}"
                if len(buttons) == 1:
                    caption += "\n😬 No Valid Trim Duration Specified."
                answers.append(
                    InlineQueryResultPhoto(
                        photo_url=f'https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg',
                        title=v["title"],
                        description=("Duration: {} Views: {}").format(
                            v["duration"],
                            v["viewCount"]["short"]
                        ),
                        caption=caption,
                        thumb_url=v["thumbnails"][0]["url"],
                        reply_markup=InlineKeyboardMarkup(buttons)
                    )
                )
                VIDEO_DICT[v['id']] = {'dur':v["duration"], 'views':v["viewCount"]["short"], 'title':v['title']}
        try:
            if start and end:
                await query.answer(
                    switch_pm_text=(f"Trim from {get_time_hh_mm_ss(start)} to {get_time_hh_mm_ss(end)}"),
                    switch_pm_parameter="start",
                    results=answers,
                    cache_time=0
                )
            else:
                await query.answer(
                    results=answers,
                    cache_time=0,
                    switch_pm_text=("❌ Invalid Time Selected"),
                    switch_pm_parameter="help",
                )
        except errors.QueryIdInvalid:
            await query.answer(
                results=answers,
                cache_time=0,
                switch_pm_text=("Nothing found"),
                switch_pm_parameter="help",
            )


__handlers__ = [
    [
        InlineQueryHandler(
            search
        )
    ]
]
