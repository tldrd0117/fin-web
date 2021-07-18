from datetime import datetime


def getNowDateStr() -> str:
    now = datetime.now()
    nowDate = now.strftime('%Y%m%d')
    return nowDate


def getNow() -> datetime:
    return datetime.now()
