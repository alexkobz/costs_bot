class CustomDateException(Exception):
    """Error selecting date"""
    pass


class StartDateException(CustomDateException):
    """Error selecting start date"""
    pass


class EndDateException(CustomDateException):
    """Error selecting end date"""
    pass
