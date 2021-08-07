from typing import Dict, List
from pydantic import BaseModel


class SocketResponse(BaseModel):
    event: str
    payload: dict


class StockTaskState(BaseModel):
    stocks: List
    years: Dict


class StockCrawlingRunCrawlingDTO(BaseModel):
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
    day: str
    hour: str
    minute: str
    second: str


class StockTaskScheduleInfo(BaseModel):
    id: str = ""
    year: str
    month: str
    day: str
    hour: str
    minute: str
    second: str
    taskList: List[StockCrawlingRunCrawlingDTO] = []


class StockTaskScheduleList(BaseModel):
    list: List[StockTaskSchedule]


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


class StockCrawlingTasksDTO(BaseModel):
    tasks: dict = dict()
    taskIds: List[str] = []


class StockCrawlingCompletedTasksDTO(BaseModel):
    history: dict = dict()
    historyIds: List[str] = []


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


class StockMarketCapitalResultDTO(BaseModel):
    data: List[StockMarketCapitalDTO] = []
    date: str = ""
    market: str = ""
    result: str = "fail"
    errorMsg: str = ""
