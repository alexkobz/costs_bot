from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from exceptions.NotCorrectMessage import EditExpenseMessageException
from helpers.BotDB import BotDB, Expense
from helpers.Form import Form


router = Router()
@router.message(Command('editid', prefix="/"))
async def on_edit_id(message: Message, state: FSMContext):
    """Редактировать расход по идентификатору"""
    await message.answer("Please write according to this template: id amount category\nfor example: 23 100 taxi")
    await state.set_state(Form.edit)


@router.message(Form.edit)
async def edit(message: Message, state: FSMContext):
    """Редактировать расход по идентификатору"""
    user: User = message.from_user
    cursor: BotDB = BotDB(user=user)
    try:
        await state.update_data(edit=message.text)
        expense: Expense = await cursor.edit_expense(message)
    except EditExpenseMessageException as e:
        await message.answer(str(e))
        return
    except Exception:
        await message.answer("Something went wrong")
        return
    finally:
        await state.clear()
        cursor.close()
        cursor.connection.close()
    row_id: int = expense.row_id
    answer_message: str = f"Edited expense with id {row_id}" if row_id != -1 else "There is no cost with this id"
    await message.answer(answer_message)
