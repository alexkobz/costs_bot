from typing import List
from prettytable import PrettyTable

from aiogram import Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, User
from helpers.BotDB import BotDB, Expense


router = Router()

@router.message(Command('last', prefix="/"))
async def on_last(message: Message):
    """Show last 10 costs"""
    user: User = message.from_user
    cursor: BotDB = BotDB(user=user)
    try:
        expenses: List[Expense] = await cursor.get_last()
    except Exception:
        await message.answer("Something went wrong")
        return
    finally:
        cursor.close()
        cursor.connection.close()

    if not expenses:
        await message.answer("There are no costs")
        return

    table = PrettyTable(['Category', 'Amount', 'Created'])
    table.align['Category'], table.align['Amount'], table.align['Created'] = 'l', 'l', 'l'
    for expense in expenses:
        table.add_row([f"{expense.category.title()}", expense.amount, expense.created])

    await message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
