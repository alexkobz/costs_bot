from datetime import date
from typing import Dict, Any

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User
from aiogram_calendar import SimpleCalendarCallback, SimpleCalendar
from aiogram_calendar.simple_calendar import SimpleCalAct

from exceptions.CustomDateException import StartDateException, EndDateException
from helpers.Form import Form
from helpers.get_now import get_today
from helpers.get_utc_offset import get_utc_offset
from helpers.report import report


router = Router()

@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(Form.date_start))
async def process_custom_start_date(call: CallbackQuery, callback_data: CallbackData, state: FSMContext):
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
    match callback_data.act:
        case SimpleCalAct.ignore:
            return
        case SimpleCalAct.prev_y:
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=callback_data.year-1, month=callback_data.month)
            )
            await state.set_state(Form.date_start)
            return
        case SimpleCalAct.next_y:
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=callback_data.year+1, month=callback_data.month)
            )
            await state.set_state(Form.date_start)
            return
        case SimpleCalAct.prev_m:
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=callback_data.year, month=callback_data.month-1)
            )
            await state.set_state(Form.date_start)
            return
        case SimpleCalAct.next_m:
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=callback_data.year, month=callback_data.month+1)
            )
            await state.set_state(Form.date_start)
            return
        case SimpleCalAct.cancel:
            await call.message.delete()
            await state.clear()
            return
        case SimpleCalAct.today:
            date_start: date = today
        case SimpleCalAct.day:
            date_start: date = date(callback_data.year, callback_data.month, callback_data.day)
        case _:
            raise StartDateException("Start date selection error")

    await state.update_data(date_start=date_start)
    await call.message.delete()
    await call.message.answer(
        "Please select a finish date:",
        reply_markup=await SimpleCalendar().start_calendar(year=today.year, month=today.month)
    )
    await state.set_state(Form.date_finish)


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(Form.date_finish))
async def process_custom_finish_date(call: CallbackQuery, callback_data: CallbackData, state: FSMContext):

    match callback_data.act:
        case SimpleCalAct.ignore:
            return
        case SimpleCalAct.prev_y:
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=callback_data.year-1, month=callback_data.month)
            )
            await state.set_state(Form.date_start)
            return
        case SimpleCalAct.next_y:
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=callback_data.year+1, month=callback_data.month)
            )
            await state.set_state(Form.date_start)
            return
        case SimpleCalAct.prev_m:
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=callback_data.year, month=callback_data.month-1)
            )
            await state.set_state(Form.date_start)
            return
        case SimpleCalAct.next_m:
            await call.message.delete()
            await call.message.answer(
                "Please select a start date:",
                reply_markup=await SimpleCalendar().start_calendar(year=callback_data.year, month=callback_data.month+1)
            )
            await state.set_state(Form.date_start)
            return
        case SimpleCalAct.cancel:
            await call.message.delete()
            await state.clear()
            return
        case SimpleCalAct.today:
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
        case SimpleCalAct.day:
            date_finish: date = date(callback_data.year, callback_data.month, callback_data.day)
        case _:
            raise EndDateException("End date selection error")

    state_data: Dict[str, Any] = await state.get_data()
    date_start: date = state_data.get("date_start", date(2022, 1, 1))

    await state.clear()
    await call.message.delete()
    await report(call, state, date_start, date_finish)
