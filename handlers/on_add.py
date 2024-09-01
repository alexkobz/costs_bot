import logging

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, User

from exceptions.NotCorrectMessage import AddExpenseMessageException
from helpers.BotDB import BotDB, Expense
from helpers.Form import Form
from helpers.get_utc_offset import get_utc_offset


router = Router()

@router.message(Command('add', prefix="/"))
async def on_add(message: Message, state: FSMContext):
    """Добавить расход"""
    await message.answer("Please write according to this template: amount category\nFor example: 100 taxi")
    await state.set_state(Form.add)


@router.message(StateFilter(Form.add))
@router.message(~F.text.startswith("/"), StateFilter(default_state))
async def add(message: Message, state: FSMContext):
    """Добавить расход"""
    user: User = message.from_user
    try:
        utc_offset_minutes, answer_message, builder = await get_utc_offset(user=user)
    except Exception as e:
        await message.answer(str(e))
        return
    if utc_offset_minutes is None:
        await message.answer(text=answer_message, reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(Form.utc_offset)
        return

    cursor: BotDB = BotDB(user=user)
    try:
        await state.update_data(add=message.text)
        expense: Expense = await cursor.add_expense(message, utc_offset_minutes)
    except AddExpenseMessageException as e:
        await message.answer(str(e))
        return
    except Exception as e:
        logging.exception(str(e))
        await message.answer(str(e))
        return
    finally:
        await state.clear()
        cursor.close()
        cursor.connection.close()
    answer_message: str = f"Added costs {expense.amount} for {expense.category} with id {expense.row_id}"
    await message.answer(answer_message)
