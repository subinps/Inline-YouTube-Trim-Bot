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
from datetime import timedelta
from math import log, floor
import json
from pyrogram.types import InlineKeyboardButton
import time
VIDEO_DICT = {}

async def get_link(id):
    ytdl_cmd = [ "yt-dlp", "--geo-bypass", "-g", "-f", "best[height<=?720][width<=?1280]/best", f"https://youtu.be/{id}"]
    process = await asyncio.create_subprocess_exec(
        *ytdl_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    output, err = await process.communicate()
    if not output:
        return False
    stream = output.decode().strip()
    link = (stream.split("\n"))[-1]
    if link:
        return link
    else:
        return False

async def trim_video(file, start, end, out, thumb):
    dur = str(int(end) - int(start))
    ffprobe_cmd = ['ffmpeg', '-ss', start, '-to', end, '-i', file, '-map', '0', '-c', 'copy', out]
    process = await asyncio.create_subprocess_exec(
        *ffprobe_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    ssgen_command = ['ffmpeg', '-i', out, '-vframes', '1', '-q:v', '2', thumb]
    s_process = await asyncio.create_subprocess_exec(
        *ssgen_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    output = await s_process.communicate()
    return file

async def get_height_and_width(file):
    ffprobe_cmd = ["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height", "-of", "json", file]
    process = await asyncio.create_subprocess_exec(
        *ffprobe_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    output, err = await process.communicate()
    stream = output.decode('utf-8')
    out = json.loads(stream)
    try:
        n = out.get("streams")
        if not n:
            width, height = 1280, 720
        else:
            width=n[0].get("width")
            height=n[0].get("height")
    except Exception as e:
        width, height = 1280, 720
    return width, height

async def progress_bar(current, total, client, start, id, caption):
    now = time.time()
    if total == 0:
        return
    if round((now - start) % 3) == 0 or current == total:
        speed = current / (now - start)
        percentage = current * 100 / total
        time_to_complete = round(((total - current) / speed))
        time_to_complete = TimeFormatter(time_to_complete) * 1000
        current_message = f"\n\n**Uploading To Telegram** {round(percentage, 2)}% @ {humanbytes(speed)}/s ⬆️ {humanbytes(current)} / {humanbytes(total)} 🕰 {time_to_complete}"
        try:
            await client.edit_inline_caption(inline_message_id = id, caption=caption + current_message)
        except:
            pass

def get_time(time):
    if time is None:
        time = "0"
    time = str(time)
    time = time.strip()
    final=[]
    if ":" not in time:
        if not time.isnumeric():
            return False
        final = [0, 0] + [time]
    elif len(time.split(":")) == 2:
        final = [0] + time.split(":")
    elif len(time.split(":")) == 3:
        final = time.split(":")
    else:
        return False
    try:
        out = sum(x * int(t) for x, t in zip([3600, 60, 1], final))
    except:
        return False
    else:
        return out

def get_time_hh_mm_ss(sec):
    sec = int(sec)
    return str(timedelta(seconds=sec))



def short_num(number):
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return  '%.2f%s' % (round(int(number) / k**magnitude, 2), units[magnitude])

def get_buttons(start, end, dur, vid_id, user, query):
    if start and end \
        and int(start) <= int(end) <= int(dur):
        return [
            [
                InlineKeyboardButton(
                    f"Trim from {get_time_hh_mm_ss(start)} to {get_time_hh_mm_ss(end)}",
                    callback_data=f"trim:{start}:{end}:{vid_id}:{user}",
                ),
            ],
            [
                InlineKeyboardButton('Search Agian', switch_inline_query_current_chat=query),
            ],
        ]

    else:
        return [
            [
                InlineKeyboardButton('Search Agian', switch_inline_query_current_chat=query)
            ]
        ]

def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + " days, ") if days else "") + \
        ((str(hours) + " hours, ") if hours else "") + \
        ((str(minutes) + " min, ") if minutes else "") + \
        ((str(seconds) + " sec, ") if seconds else "") + \
        ((str(milliseconds) + " millisec, ") if milliseconds else "")
    return tmp[:-2]