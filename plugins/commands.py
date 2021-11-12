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

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_message(filters.command("start"))
async def start(bot, message):
    buttons = [
            [
                InlineKeyboardButton('Search Here', switch_inline_query_current_chat=""),
            ],
            [
                InlineKeyboardButton('Updates', url="https://t.me/subin_works")
            ]
        ]
    await message.reply(
        f"**Hey {message.from_user.mention},\nIam an Inline Youtube Trimmer.**\n__You can use me only via inline mode.__\n\nExample: `@TrimYtbot Niram | 1:25:1 1:26:6` or `@TrimYtbot Niram | 1800 2000`",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_message(filters.command("help"))
async def help(bot, message):
    await start()

@Client.on_message(filters.private & filters.text & ~filters.via_bot)
async def text_msgs(bot, message):
    buttons = [
            [
                InlineKeyboardButton('Search Inline', switch_inline_query_current_chat=message.text),
            ],
        ]
    await message.reply(
        "Hey I can work only via inline.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )