""" Работа с расходами — их добавление, удаление, статистики"""
from os import environ
import psycopg
import pandas as pd
from typing import List, NamedTuple, Tuple, Optional
from datetime import date, datetime as dt

from aiogram.types import Message, User

from helpers.get_now import get_now
from helpers.parse_message import (Parsed_Add_Expense_Message,
                                   Parsed_Delete_Expense_Message,
                                   Parsed_Edit_Expense_Message,
                                   parse_delete_expense_message,
                                   parse_add_expense_message,
                                   parse_edit_expense_message)


class Expense(NamedTuple):
    """Структура расхода"""
    row_id: int
    user_id: int
    message_id: int
    amount: float
    category: str
    created: date



class BotDB(psycopg.Cursor):

    def __init__(self, user: User):
        super().__init__(psycopg.connect(
            f"dbname={environ['POSTGRES_DB']} "
            f"user={environ['POSTGRES_USER']} "
            f"password={environ['POSTGRES_PASSWORD']} "
            f"host={environ['POSTGRES_HOST']} "
            f"port={environ['POSTGRES_PORT']}")
        )
        self.user = user

    async def get_utc_offset(self) -> Tuple[Optional[int]]:
        return self.execute("SELECT utc_offset FROM users WHERE id = %s;", (self.user.id,)).fetchone()

    async def user_exists(self) -> bool:
        user_exists: int = self.execute(
            f"SELECT EXISTS (SELECT utc_offset FROM users WHERE id = %s);", (self.user.id,)
        ).fetchone()[0]
        return user_exists != 0

    async def create_user(self, utc_offset_minutes: int) -> str:
        user_exists = await self.user_exists()
        if not user_exists:
            added_date: dt = await get_now(utc_offset_minutes)
            self.execute("INSERT INTO users (id, first_name, is_bot, language_code, added_date, utc_offset) VALUES (%s, %s, %s, %s, %s, %s);",
                         (self.user.id, self.user.first_name.replace("'", "").replace('"', ""), self.user.is_bot,
                          self.user.language_code, added_date, utc_offset_minutes,))
        else:
            self.execute(
                f"UPDATE users SET first_name = %s, is_bot = %s, language_code = %s, utc_offset = %s WHERE id = %s;",
                (self.user.first_name.replace("'", "").replace('"', ""), self.user.is_bot, self.user.language_code, utc_offset_minutes, self.user.id,)
            )
        self.connection.commit()
        return "Updated" if user_exists else f"""Hello, {self.user.first_name.replace("'", "").replace('"', "")}"""

    async def add_expense(self, message: Message, utc_offset_minutes: int) -> Expense:
        """Добавляет новый расход.
        Принимает на вход текст сообщения, пришедшего в бот."""
        parsed_message: Parsed_Add_Expense_Message = await parse_add_expense_message(message.text)
        created: dt = await get_now(utc_offset_minutes)
        row: tuple = self.execute(
            """
            INSERT INTO costs (user_id, message_id, amount, category, created) 
            VALUES (%s, %s, %s, %s, %s) RETURNING *;""",
            (self.user.id, message.message_id, parsed_message.amount, parsed_message.category, created,)
        ).fetchone()
        row_id, user_id, message_id, amount, category, created = row
        self.connection.commit()
        return Expense(row_id, user_id, message_id, amount, category, created)

    async def delete_expense(self, message=None) -> Expense:
        """Удаляет сообщение по его идентификатору"""
        if message is None:
            row_id: Tuple[Optional[int]] = self.execute(
                f"SELECT max(id) FROM costs WHERE user_id = %s;",
                (self.user.id,)
            ).fetchone()
            if not row_id:
                return Expense(-1, -1, -1, -1, "", date(1900, 1, 1))
            else:
                row_id: int = row_id[0]
        else:
            parsed_message: Parsed_Delete_Expense_Message = await parse_delete_expense_message(raw_message=message.text)
            row_id: int = parsed_message.row_id
        row: Optional[tuple] = self.execute(
            f"DELETE FROM costs WHERE id = %s RETURNING *;",
            (row_id, )
        ).fetchone()
        self.connection.commit()
        if row:
            row_id, user_id, message_id, amount, category, created = row
            return Expense(row_id, user_id, message_id, amount, category, created)
        else:
            return Expense(-1, -1, -1, -1, "", date(1900, 1, 1))

    async def edit_expense(self, message: Message) -> Expense:
        """Удаляет сообщение по его идентификатору"""
        parsed_message: Parsed_Edit_Expense_Message = await parse_edit_expense_message(raw_message=message.text)
        row_id, amount, category = parsed_message.row_id, parsed_message.amount, parsed_message.category
        exists: bool = self.execute(
            f"""SELECT EXISTS (SELECT 1 FROM costs WHERE user_id = %s AND id = %s);""",
            (self.user.id, row_id,)
        ).fetchone()
        if not exists:
            return Expense(-1, -1, -1, -1, "", date(1900, 1, 1))
        else:
            row: Optional[tuple] = self.execute(
                f"""UPDATE costs SET amount = %s, category = %s WHERE user_id = %s AND id = %s RETURNING *;""",
                (amount, category, self.user.id, row_id)
            ).fetchone()
            self.connection.commit()
            if row:
                row_id, user_id, message_id, amount, category, created = row
                return Expense(row_id, user_id, message_id, amount, category, created)
            else:
                return Expense(-1, -1, -1, -1, "", date(1900, 1, 1))

    async def get_report(self, date_start: date, date_finish: date) -> pd.DataFrame:
        date_start, date_finish = date_start.strftime("%Y-%m-%d"), date_finish.strftime("%Y-%m-%d")
        self.execute(
            """
            SELECT created as Created, category AS Category, amount AS Amount, id 
            FROM "costs"
            WHERE user_id = %s AND date(created) BETWEEN %s AND %s;""",
            params=(self.user.id, date_start, date_finish,)
        )
        report_df: pd.DataFrame = pd.DataFrame(self.fetchall(), columns=["Created", "Category", "Amount", "id"])
        return report_df

    async def get_last(self) -> List[Expense]:
        """Возвращает последние несколько расходов"""
        rows: list = self.execute(
            """
            SELECT id, user_id, message_id, amount, category, date(created) as created
            FROM costs 
            WHERE user_id = %s
            ORDER BY created DESC LIMIT 10;""",
            (self.user.id,)
        ).fetchall()
        last_expenses: List[Expense] = [Expense(row_id=row[0],
                                                user_id=row[1],
                                                message_id=row[2],
                                                amount=row[3],
                                                category=row[4],
                                                created=row[5]) for row in rows]
        return last_expenses
