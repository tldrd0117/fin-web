from pydantic import BaseModel
from collections import deque


class StockCrawlingRunCrawlingDTO(BaseModel):
    driverAddr: str
    market: str
    startDateStr: str
    endDateStr: str
    taskId: str
    taskUniqueId: str


class StockCrawlingDownloadTaskDTO(BaseModel):
    uuid: str
    market: str
    dateStr: str
    taskId: str
    taskUniqueId: str


class StockCrawlingTaskDTO(BaseModel):
    count: int = 0
    successCount: int = 0
    failCount: int = 0
    restCount: int = 0
    failTasks: deque = deque()
    state: str = "stop"
    tasks: deque = deque()
    tasksRet: deque = deque()
    index: int = 0
    market: str = ""
    startDateStr: str = ""
    endDateStr: str = ""
    taskUniqueId: str = ""
    percent: float = 0.0
    taskId: str = ""


class StockCrawlingTasksDTO(BaseModel):
    tasks: dict = dict()
    taskIds: deque = deque()


class StockMarketCapitalDTO(BaseModel):
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
    createdAt: str
    updatedAt: str


class StockMarketCapitalResultDTO(BaseModel):
    data: deque = deque()
    date: str = ""
    market: str = ""
    result: str = "fail"
    errorMsg: str = ""



