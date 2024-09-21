from datetime import date, timedelta

from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, User, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_calendar import SimpleCalendar
from pandas.tseries import offsets

from helpers.Form import Form
from helpers.dicts import excel_period
from helpers.excel_report import excel_report
from helpers.get_now import get_today
from helpers.get_utc_offset import get_utc_offset

router = Router()


@router.message(Command('excel', prefix="/"))
async def on_excel(message: Message, state: FSMContext):
    """To export the costs to excel file"""
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for period in excel_period:
        builder.add(InlineKeyboardButton(callback_data=period, text=excel_period[period]))
    builder.adjust(2)
    await message.answer(text="Select period:",
                         reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(Form.date_start_excel)


@router.callback_query(F.data.startswith("excel_"), StateFilter(Form.date_start_excel))
async def excel_period_callback(call: CallbackQuery, state: FSMContext):
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
        case "excel_today":
            date_start: date = today
        case "excel_yesterday":
            date_start: date = today - timedelta(days=1)
            date_finish = date_start
        case "excel_week":
            date_start: date = today - timedelta(days=today.weekday())
        case "excel_month":
            date_start: date = (today - offsets.MonthBegin(n=1)).to_pydatetime().date()
        case "excel_all":
            date_start: date = date(1900, 1, 1)
            date_finish: date = date(9999, 1, 1)
        case "excel_custom":
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=today.year, month=today.month)
            )
            await state.set_state(Form.date_start_excel)
            return
        case _:
            await call.message.delete()
            raise Exception

    await state.clear()
    await call.message.delete()
    await excel_report(call, state, date_start, date_finish)
