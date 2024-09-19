from datetime import datetime as dt, timedelta, timezone, date


async def get_now(utc_offset_minutes: int) -> dt:
    """Возвращает сегодняшний datetime с учётом временной зоны"""
    return dt.now(tz=timezone(timedelta(minutes=utc_offset_minutes)))


async def get_today(utc_offset_minutes: int) -> date:
    """Возвращает сегодняшний date с учётом временной зоны"""
    return (dt.now(tz=timezone(timedelta(minutes=utc_offset_minutes)))).date()


async def get_now_str(utc_offset_minutes: int) -> str:
    """Возвращает сегодняшний datetime с учётом временной зоны"""
    now = await get_now(utc_offset_minutes)
    return now.strftime("%Y-%m-%d %H:%M:%S")


async def get_today_str(utc_offset_minutes: int) -> str:
    """Возвращает сегодняшний date с учётом временной зоны"""
    today: date = await get_today(utc_offset_minutes)
    return today.strftime("%Y-%m-%d")
