from typing import Tuple

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from helpers.dicts import timezones


async def build_inline_keyboard_utc_offset() -> Tuple[str, InlineKeyboardBuilder]:
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for tz in timezones:
        builder.add(InlineKeyboardButton(callback_data=tz, text=tz))
    builder.adjust(2)
    answer_message: str = "I need to know just one thing - your timezone"
    return answer_message, builder

