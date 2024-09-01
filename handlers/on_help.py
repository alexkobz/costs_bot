from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command('help', prefix="/"))
async def on_help(message: Message):
    """Отправляет помощь по боту"""
    await message.answer(
        "Бот для учёта расходов\n\n"
        "Показать описание с помощью команды /help\n"
        "Добавить расход с помощью команды /add или написать сообщение по шаблону: 100 продукты\n"
        "Удалить последний расход /delete\n"
        "Удалить расход по идентификатору /deleteid\n"
        "Редактировать расход по идентификатору /editid\n"
        "Показать отчет /report\n"
        "Выгрузить расходы в excel /excel\n"
        "Показать последние 10 внесённых расходов /last")
