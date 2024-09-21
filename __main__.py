"""
Name: CostsBot
About: Cost accounting
Description: The bot can add/delete costs and make reports
Description picture: 🚫 no description picture
Botpic: 🖼 has a botpic
Commands: 8 commands
Privacy Policy: 🚫
Commands:
    /add - Add the cost
    /delete - Delete the last cost
    /deleteid - Delete the cost by id
    /editid - Edit the cost by id
    /report - Show report
    /excel - Export report in Excel file
    /last - Show the last 10 costs
    /help - Show help
    /cancel - Cancel command
"""

__author__ = "Alexander Kobzar"
__contact__ = "alexanderkobzarrr@gmail.com"
__github__ = "alexkobz"
__maintainer__ = "developer"
__created__ = "01-09-2024"
__modified__ = "21-09-2024"
__status__ = "Production"
__version__ = "1.0.2"

import asyncio
import logging
import os
from typing import List

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import (on_add, on_delete, on_delete_id, on_edit_id, on_excel, on_help, on_last, on_report, on_start,
                      on_cancel, process_custom_date, utc_offset)


async def main() -> None:
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    TOKEN: str = os.environ['TOKEN']
    bot: Bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='html'))
    storage: MemoryStorage = MemoryStorage()
    dp: Dispatcher = Dispatcher(storage=storage)
    routers: List[Router] = [
        on_start.router,
        on_add.router,
        on_delete.router,
        on_delete_id.router,
        on_edit_id.router,
        on_excel.router,
        on_help.router,
        on_last.router,
        on_report.router,
        on_cancel.router,
        process_custom_date.router,
        utc_offset.router
    ]
    dp.include_routers(*routers)
    try:
        logger.info("Started")
        await dp.start_polling(bot)
    finally:
        logger.info("Shutdown")


if __name__ == '__main__':
    asyncio.run(main())
