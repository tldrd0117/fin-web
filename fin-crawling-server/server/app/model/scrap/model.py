from typing import List
from pydantic import BaseModel


class RunScrap(BaseModel):
    taskId: str
    taskUniqueId: str


class SeibroDividendRunScrap(RunScrap):
    driverAddr: str
    codes: List     # 종목코드 리스트
    startDate: str  # 시작날짜
    endDate: str    # 종료날짜


class SeibroStockNumRunScrap(RunScrap):
    driverAddr: str
    codes: List     # 종목코드 리스트
    startDate: str  # 시작날짜
    endDate: str    # 종료날짜


class MarcapRunScrap(RunScrap):
    driverAddr: str
    market: str
    startDateStr: str
    endDateStr: str
    isNow: bool = False


class FactorDartRunScrap(RunScrap):
    apiKey: str
    isCodeNew: bool
    startYear: int
    endYear: int


class FactorFileRunScrap(RunScrap):
    pass
