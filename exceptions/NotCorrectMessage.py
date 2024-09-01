class NotCorrectMessage(Exception):
    """Некорректное сообщение в бот, которое не удалось распарсить"""
    pass


class AddExpenseMessageException(NotCorrectMessage):
    """Некорректное сообщение о добавлении расхода"""
    pass


class DeleteExpenseMessageException(NotCorrectMessage):
    """Некорректное сообщение об удалении расхода"""
    pass


class EditExpenseMessageException(NotCorrectMessage):
    """Некорректное сообщение о редактировании расхода"""
    pass
