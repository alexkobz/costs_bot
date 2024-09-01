class CustomDateException(Exception):
    """Ошибка в выборе даты"""
    pass


class StartDateException(CustomDateException):
    """Ошибка в выборе начальной даты"""
    pass


class EndDateException(CustomDateException):
    """Ошибка в выборе конечной даты"""
    pass
