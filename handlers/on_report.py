from datetime import date, timedelta

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_calendar import SimpleCalendar
from pandas.tseries import offsets

from helpers.Form import Form
from helpers.dicts import report_period
from helpers.get_now import get_today
from helpers.get_utc_offset import get_utc_offset
from helpers.report import report


router = Router()

@router.message(Command('report', prefix="/"))
async def on_report(message: Message, state: FSMContext):
    """Show report"""
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for period in report_period:
        builder.add(InlineKeyboardButton(callback_data=period, text=report_period[period]))
    await message.answer(text="Select period:",
                         reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Form.date_start)


@router.callback_query(F.data.startswith("report_"), StateFilter(Form.date_start))
async def report_period_callback(call: CallbackQuery, state: FSMContext):
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

    today: date = await get_today(utc_offset_minutes=utc_offset_minutes)
    date_finish: date = today
    match call.data:
        case "report_today":
            date_start: date = today
        case "report_yesterday":
            date_start: date = today - timedelta(days=1)
            date_finish = date_start
        case "report_week":
            date_start: date = today - timedelta(days=today.weekday())
        case "report_month":
            date_start: date = (today - offsets.MonthBegin(n=1)).to_pydatetime().date()
        case "report_custom":
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=today.year, month=today.month)
            )
            await state.set_state(Form.date_start)
            return
        case _:
            raise Exception

    await state.clear()
    await call.message.delete()
    await report(call, state, date_start, date_finish)
