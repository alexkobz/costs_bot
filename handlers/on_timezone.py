from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from helpers.Form import Form
from helpers.build_inline_keyboard_utc_offset import build_inline_keyboard_utc_offset


router = Router()

@router.message(Command("timezone", prefix="/"))
async def on_timezone(message: Message, state: FSMContext):
    """Change the timezone"""
    await state.clear()
    answer_message, builder = await build_inline_keyboard_utc_offset()
    await message.answer(text=answer_message, reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Form.utc_offset)
