import pandas as pd
from datetime import date
from matplotlib.axes._axes import Axes
from matplotlib.figure import Figure
from prettytable import PrettyTable
from psycopg import OperationalError

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, User

from helpers.BotDB import BotDB
from helpers.Form import Form
from helpers.get_utc_offset import get_utc_offset


async def report(call: CallbackQuery, state: FSMContext,
                 date_start=date(2000, 1, 1), date_finish=date(9999, 1, 1)):
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
    except Exception as e:
        await call.message.answer(str(e))
        return
    finally:
        cursor.close()
        cursor.connection.close()
        await state.clear()

    if report_df.empty:
        answer_message: str = "There are no costs"
        await call.message.answer(text=answer_message)
    else:
        report_sum_all: int = report_df["Amount"].sum()
        report_sum_10: pd.Series = report_df.groupby("Category")["Amount"].sum().sort_values()
        report_sum_10: pd.Series = report_sum_10.astype(float)

        title: str = f"Report for {date_start} - {date_finish}" if date_start != date_finish else f"Report for {date_start}"
        title += f"\nOverall: {report_sum_all}"
        ax: Axes = report_sum_10.plot.barh(
            grid=True,
            xlabel="Amount",
            ylabel="Category",
            title=title,
            figsize=(10, 6)
        )
        ax.bar_label(ax.containers[0])
        fig: Figure = ax.get_figure()
        fname: str = f'report.png'
        fig.savefig(fname, dpi=300)
        report_file: FSInputFile = FSInputFile(fname)
        fig.clf()
        await call.message.answer_photo(report_file)

        table = PrettyTable(['Category', 'Amount'])
        table.align['Category'], table.align['Amount'] = 'l', 'l'
        report_dict: dict = report_sum_10.to_dict()
        for expense in reversed(report_dict.items()):
            table.add_row([f"{expense[0].title()}", expense[1]])
        table.add_row(["OVERALL", report_sum_all])
        await call.message.answer(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
