from typing import Any, Dict, List
from pydantic import BaseModel


class SocketResponse(BaseModel):
    event: str
    payload: dict


class ListLimitData(BaseModel):
    offset: int
    limit: int


class StockTaskState(BaseModel):
    market: str
    taskId: str
    stocks: List
    years: Dict


class StockUpdateState(BaseModel):
    market: str
    taskId: str
    date: str
    ret: str


class YearData(BaseModel):
    yearData: Dict[str, Dict]


class ListLimitResponse(BaseModel):
    data: Any
    offset: int
    limit: int
    count: int


class StockCrawlingRunCrawling(BaseModel):
    driverAddr: str
    market: str
    startDateStr: str
    endDateStr: str
    taskId: str
    taskUniqueId: str


class StockTaskSchedule(BaseModel):
    id: str = ""
    year: str
    month: str
    dayOfWeek: str
    day: str
    hour: str
    minute: str
    second: str


class StockTaskScheduleInfo(BaseModel):
    id: str = ""
    year: str
    month: str
    dayOfWeek: str
    day: str
    hour: str
    minute: str
    second: str
    taskList: List[StockCrawlingRunCrawling] = []


class StockTaskScheduleList(BaseModel):
    list: List[StockTaskSchedule]


class StockCrawlingDownloadTask(BaseModel):
    uuid: str
    market: str
    dateStr: str
    taskId: str
    taskUniqueId: str


class StockCrawlingTask(BaseModel):
    count: int = 0
    successCount: int = 0
    failCount: int = 0
    restCount: int = 0
    failTasks: List[str] = []
    state: str = "stop"
    tasks: List[str] = []
    tasksRet: List[int] = []
    index: int = 0
    market: str = ""
    startDateStr: str = ""
    endDateStr: str = ""
    taskUniqueId: str = ""
    percent: float = 0.0
    taskId: str = ""
    errMsg: str = ""


class StockCrawlingTasks(BaseModel):
    tasks: dict = dict()
    taskIds: List[str] = []


class StockCrawlingCompletedTasks(BaseModel):
    history: dict = dict()
    historyIds: List[str] = []


class StockMarketCapital(BaseModel):
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


class StockMarketCapitalResult(BaseModel):
    data: List[StockMarketCapital] = []
    date: str = ""
    market: str = ""
    result: str = "fail"
    errorMsg: str = ""


class StockMarketCapitalResponse(BaseModel):
    list: List[StockMarketCapital]
    count: int
