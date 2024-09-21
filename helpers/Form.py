from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    utc_offset = State()
    add = State()
    edit = State()
    delete = State()
    date_start_report = State()
    date_start_excel = State()
    date_finish_report = State()
    date_finish_excel = State()
