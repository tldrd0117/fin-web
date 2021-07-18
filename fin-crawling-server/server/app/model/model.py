from pydantic import BaseModel


class StockCrawlingRunCrawling(BaseModel):
    driverAddr: str
    market: str
    startDateStr: str
    endDateStr: str
    taskId: str
    taskUniqueId: str
