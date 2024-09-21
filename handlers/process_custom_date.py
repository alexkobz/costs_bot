from datetime import date
from typing import Dict, Any

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendarCallback

from helpers.Form import Form
from helpers.excel_report import excel_report
from helpers.process_custom_date import process_custom_start_date, process_custom_finish_date
from helpers.report import report


router = Router()

@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(Form.date_start_report))
async def on_custom_start_date_report(call: CallbackQuery,
                                      callback_data: CallbackData,
                                      state: FSMContext):
    date_start = await process_custom_start_date(call, callback_data, state)
    await state.update_data(date_start_report=date_start)
    await state.set_state(Form.date_finish_report)


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(Form.date_finish_report))
async def on_custom_finish_date_report(call: CallbackQuery,
                                       callback_data: CallbackData,
                                       state: FSMContext):

    date_finish: date = await process_custom_finish_date(call, callback_data, state)
    state_data: Dict[str, Any] = await state.get_data()
    date_start: date = state_data.get("date_start_report", date(1900, 1, 1))

    await state.clear()
    await call.message.delete()
    await report(call, state, date_start, date_finish)


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(Form.date_start_excel))
async def on_custom_start_date_excel(call: CallbackQuery,
                                     callback_data: CallbackData,
                                     state: FSMContext):
    date_start = await process_custom_start_date(call, callback_data, state)
    await state.update_data(date_start_excel=date_start)
    await state.set_state(Form.date_finish_excel)


@router.callback_query(SimpleCalendarCallback.filter(), StateFilter(Form.date_finish_excel))
async def on_custom_finish_date_excel(call: CallbackQuery,
                                      callback_data: CallbackData,
                                      state: FSMContext):

    date_finish: date = await process_custom_finish_date(call, callback_data, state)
    state_data: Dict[str, Any] = await state.get_data()
    date_start: date = state_data.get("date_start_excel", date(1900, 1, 1))

    await state.clear()
    await call.message.delete()
    await excel_report(call, state, date_start, date_finish)
