from datetime import date

import pandas as pd
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User, FSInputFile
from psycopg import OperationalError

from helpers.BotDB import BotDB
from helpers.Form import Form
from helpers.get_utc_offset import get_utc_offset


async def excel_report(call: CallbackQuery, state: FSMContext,
                       date_start=date(2022, 1, 1), date_finish=date.today()):
    user: User = call.from_user
    try:
        utc_offset_minutes, answer_message, builder = await get_utc_offset(user=user)
    except Exception:
        await call.message.answer("Something went wrong")
        return
    if utc_offset_minutes is None:
        await call.message.answer(text=answer_message, reply_markup=builder.as_markup(resize_keyboard=True))
        await state.set_state(Form.utc_offset)
        return

    cursor: BotDB = BotDB(user=user)
    try:
        report_df: pd.DataFrame = await cursor.get_report(date_start=date_start, date_finish=date_finish)
    except OperationalError:
        await call.message.answer("Please try again later")
        return
    except Exception:
        await call.message.answer("Something went wrong")
        return
    finally:
        cursor.close()
        cursor.connection.close()
        await state.clear()

    if report_df.empty:
        await call.message.answer("There are no costs")
        return
    report_df["Created"] = pd.to_datetime(report_df["Created"])
    report_df["Date"] = report_df["Created"].dt.date
    report_df["Time"] = report_df["Created"].dt.time
    report_df["Category"] = report_df["Category"].str.title()
    pivot: pd.DataFrame = pd.pivot_table(report_df, index=["Date", "Time", "Category"], values=["Amount", "id"])
    pivot["id"] = pivot["id"].astype(int)
    title: str = f"Report_{date_start}_{date_finish}.xlsx" if date_start != date_finish else f"Report_{date_start}.xlsx"
    pivot.to_excel(title)
    report_file: FSInputFile = FSInputFile(title)
    await call.message.answer_document(report_file)
