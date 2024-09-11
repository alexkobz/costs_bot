from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User

from exceptions.Cancel import Cancel
from exceptions.NotCorrectMessage import DeleteExpenseMessageException
from helpers.BotDB import BotDB, Expense
from helpers.Form import Form


router = Router()

@router.message(Command('deleteid', prefix="/"))
async def on_delete_id(message: Message, state: FSMContext):
    """To delete the last cost by id"""
    await message.answer("Please write according to this template: id\nFor example: 23")
    await state.set_state(Form.delete)


@router.message(Form.delete)
async def delete(message: Message, state: FSMContext):
    """To delete the last cost by id"""
    user: User = message.from_user
    cursor: BotDB = BotDB(user=user)
    try:
        await state.update_data(delete=message.text)
        expense: Expense = await cursor.delete_expense(message)
    except Cancel as e:
        await message.answer(str(e))
        return
    except DeleteExpenseMessageException as e:
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
    answer_message: str = f"Deleted expense with id {row_id}" if row_id != -1 else "There is no cost with this id"
    await message.answer(answer_message)
