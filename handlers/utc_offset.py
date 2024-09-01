from psycopg import OperationalError

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User

from helpers.BotDB import BotDB
from helpers.Form import Form
from helpers.dicts import timezones
from helpers.get_utc_offset import user_dict


router = Router()

@router.callback_query(F.data.startswith("UTC"), StateFilter(Form.utc_offset))
async def utc_offset(call: CallbackQuery, state: FSMContext):
    utc_offset_minutes: int = timezones[call.data]
    user: User = call.from_user
    user_dict[user.id] = utc_offset_minutes

    cursor: BotDB = BotDB(user=user)
    try:
        answer_message: str = await cursor.create_user(utc_offset_minutes=utc_offset_minutes)
    except OperationalError:
        await call.message.answer("Please try again later")
        return
    except Exception:
        await call.message.answer("Something went wrong")
        return
    finally:
        await state.clear()
        cursor.close()
        cursor.connection.close()
        await call.message.delete()
    await call.message.answer(text=answer_message)
