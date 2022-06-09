

from typing import Any, Optional
from pandas import Timestamp
import pandas as pd
from datetime import datetime, timedelta, date


def getNow():
    return datetime.now()

def getCurrentDate():
    return date.today().strftime("%Y%m%d")


def moveMonth(datetime: Timestamp, delta: int, day: Optional[int]):
    nextTime = datetime
    if day is None:
        day = datetime.day
    for _ in range(abs(delta)):
        if delta > 0:
            nextTime = nextTime + pd.Timedelta(32, unit="D")
        else:
            nextTime = nextTime.replace(day=1) + pd.Timedelta(-2, unit="D")
        nextTime = nextTime.replace(day=day)
    return nextTime


def getDateArr(startDateStr: str, endDateStr: str):
    startDate = datetime.strptime(startDateStr, "%Y%m%d")
    endDate = datetime.strptime(endDateStr, "%Y%m%d")
    taskDates = [(startDate + timedelta(days=x)).strftime("%Y%m%d") for x in range((endDate - startDate).days + 1)]
    return taskDates

def getMonthArr(startDateStr: str, endDateStr: str):
    startDate = datetime.strptime(startDateStr, "%Y%m%d")
    endDate = datetime.strptime(endDateStr, "%Y%m%d")
    taskDates = [(startDate + timedelta(days=x)).strftime("%Y%m%d") for x in range((endDate - startDate).days + 1)]
    return taskDates

def getYearArr(startDateStr: str, endDateStr: str):
    return range(int(startDateStr[0:4]), int(endDateStr[0:4])+1)