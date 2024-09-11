from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from helpers.Form import Form
from helpers.build_inline_keyboard_utc_offset import build_inline_keyboard_utc_offset
from handlers.on_help import on_help


router = Router()

@router.message(Command("start", prefix="/"))
async def on_start(message: Message, state: FSMContext):
    """To start, register the user and show the description"""
    await state.clear()
    await on_help(message)
    answer_message, builder = await build_inline_keyboard_utc_offset()
    await message.answer(text=answer_message, reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Form.utc_offset)
