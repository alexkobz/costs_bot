from re import compile as regex_compile, Pattern
from exceptions.NotCorrectMessage import (AddExpenseMessageException,
                                          DeleteExpenseMessageException,
                                          EditExpenseMessageException)
from typing import NamedTuple, List, AnyStr
from dataclasses import dataclass


@dataclass
class regex_message:
    string: str

    def __eq__(self, message: str):
        message: Pattern[AnyStr] = regex_compile(message)
        return message.fullmatch(self.string) is not None


class Parsed_Add_Expense_Message(NamedTuple):
    """Структура распаршенного сообщения о новом расходе"""
    amount: float
    category: str


class Parsed_Delete_Expense_Message(NamedTuple):
    """Структура распаршенного сообщения об удаленном расходе"""
    row_id: int


class Parsed_Edit_Expense_Message(NamedTuple):
    """Структура распаршенного сообщения о редактированном расходе"""
    row_id: int
    amount: float
    category: str


async def parse_add_expense_message(raw_message: str) -> Parsed_Add_Expense_Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    message: str = raw_message.strip()
    match regex_message(message):
        case r"(\d+(?:\.\d+)?)":
            amount: float = float(message)
            category: str = "other"
            return Parsed_Add_Expense_Message(amount, category)
        case r"(\d+(?:\.\d+)?)\s+[\w ,.;]+$":
            message: List[str] = [word.lower() for word in message.split(" ") if word]
            amount: float = float(message[0])
            category: str = " ".join(message[1:])
            return Parsed_Add_Expense_Message(amount, category)
        case _:
            raise AddExpenseMessageException("Cannot parse\nPlease write according to this template: amount category\n"
                                             "For example: 100 taxi")


async def parse_delete_expense_message(raw_message: str) -> Parsed_Delete_Expense_Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    message: str = raw_message.strip()
    match regex_message(message):
        case r"(\d+)":
            row_id: int = int(message)
            return Parsed_Delete_Expense_Message(row_id)
        case _:
            raise DeleteExpenseMessageException("Cannot parse\nPlease write according to this template: id\n"
                                                "For example: 23")


async def parse_edit_expense_message(raw_message: str) -> Parsed_Edit_Expense_Message:
    """Парсит текст пришедшего сообщения о новом расходе."""
    message: str = raw_message.strip()
    match regex_message(message):
        case r"(\d+)\s+(\d+(?:\.\d+)?)":
            message: List[str] = [word.lower() for word in message.split(" ") if word]
            row_id: int = int(message[0])
            amount: float = float(message[1])
            category: str = "other"
            return Parsed_Edit_Expense_Message(row_id, amount, category)
        case r"(\d+)\s+(\d+(?:\.\d+)?)\s+[\w ,.;]+$":
            message: List[str] = [word.lower() for word in message.split(" ") if word]
            row_id: int = int(message[0])
            amount: float = float(message[1])
            category: str = " ".join(message[2:])
            return Parsed_Edit_Expense_Message(row_id, amount, category)
        case _:
            raise EditExpenseMessageException("Cannot parse\nPlease write according to this template: "
                                              "id amount category\nFor example: 23 100 taxi")
