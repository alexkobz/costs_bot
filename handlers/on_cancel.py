from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message


router = Router()

@router.message(Command("cancel", prefix="/"), StateFilter(default_state))
async def on_cancel_empty(message: Message):
    """To cancel the action"""
    await message.answer("Nothing to cancel")


@router.message(Command("cancel", prefix="/"), ~StateFilter(default_state))
async def on_cancel(message: Message, state: FSMContext):
    """To cancel the action"""
    await state.clear()
    await message.answer("Canceled")
