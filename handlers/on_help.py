from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command('help', prefix="/"))
async def on_help(message: Message):
    """Отправляет помощь по боту"""
    await message.answer(
        "The bot is for cost accounting\n\n"
        "To show description of the bot /help\n"
        "To add the cost with command /add or just write on the template: 100 food\n"
        "To delete the last cost with command /delete\n"
        "To delete the cost by id with command /deleteid\n"
        "To edit the cost by id with command /editid\n"
        "To show the report with command /report\n"
        "To export the costs to excel file with command /excel\n"
        "To show the last 10 costs with command /last\n"
        "To cancel the action with command /cancel")
