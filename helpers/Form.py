from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    utc_offset = State()
    add = State()
    edit = State()
    delete = State()
    date_start = State()
    date_finish = State()
