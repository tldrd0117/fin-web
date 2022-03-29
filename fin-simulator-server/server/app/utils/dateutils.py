

from typing import Any, Optional
from pandas import Timestamp
import pandas as pd


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