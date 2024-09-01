from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, User

from exceptions.NotCorrectMessage import DeleteExpenseMessageException
from helpers.BotDB import BotDB, Expense

router = Router()

@router.message(Command('delete', prefix="/"))
async def on_delete(message: Message):
    """Удалить последний расход"""
    user: User = message.from_user
    cursor: BotDB = BotDB(user=user)
    try:
        expense: Expense = await cursor.delete_expense()
    except DeleteExpenseMessageException as e:
        await message.answer(str(e))
        return
    except Exception:
        await message.answer("Something went wrong")
        return
    finally:
        cursor.close()
        cursor.connection.close()
    row_id: int = expense.row_id
    answer_message: str = f"Deleted expense with id {row_id}" if row_id != -1 else f"There are no costs"
    await message.answer(answer_message)
