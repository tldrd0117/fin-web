from typing import Any
from pydantic import BaseModel
from datetime import datetime


class Dao(BaseModel):
    pass


class StockMarketCapitalDao(Dao):
    # 종목코드,종목명,종가,대비,등락률,시가,고가,저가,거래량,거래대금,시가총액,상장주식수
    date: str
    market: str
    code: str
    name: str
    close: str
    diff: str
    percent: str
    open: str
    high: str
    low: str
    volume: str
    price: str
    marcap: str
    number: str


class ListLimitDao(Dao):
    offset: int
    limit: int 


class ListLimitDataDao(Dao):
    data: Any
    offset: int
    limit: int
    count: int


class TaskDao(Dao):
    taskUniqueId: str
    taskId: str
    count: int
    createdAt: datetime
    updatedAt: datetime
    startDateStr: str
    endDateStr: str
    failCount: int
    failTasks: list
    tasksRet: list
    index: str
    market: str
    percent: int
    restCount: str
    state: str
    successCount: int


class FactorDao(Dao):
    code: str       # 종목코드
    name: str       # 종목이름
    dataYear: str   # 결산월
    dataMonth: str  # 결산년
    dataName: str   # 데이터명
    dataValue: str  # 데이터값

