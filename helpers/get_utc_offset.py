from typing import Tuple, Optional, Dict

from aiogram.types import User
from aiogram.utils.keyboard import InlineKeyboardBuilder

from helpers.BotDB import BotDB
from helpers.build_inline_keyboard_utc_offset import build_inline_keyboard_utc_offset


user_dict: Dict[int, int] = {}

async def get_utc_offset(user: User) -> Tuple[Optional[int], Optional[str], Optional[InlineKeyboardBuilder]]:
    utc_offset_minutes: Optional[int] = user_dict.get(user.id, None)
    if utc_offset_minutes is None:
        cursor: BotDB = BotDB(user=user)
        try:
            utc_offset_minutes: Tuple[Optional[int]] = await cursor.get_utc_offset()
            if utc_offset_minutes is None:
                message, builder = await build_inline_keyboard_utc_offset()
                answer_message: str = "We cannot handle your message because we do not know your timezone\n" + message
                return None, answer_message, builder
            else:
                utc_offset_minutes: int = utc_offset_minutes[0]
                user_dict[user.id] = utc_offset_minutes
        finally:
            cursor.close()
            cursor.connection.close()
    return utc_offset_minutes, None, None
