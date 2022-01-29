from fastapi import WebSocket

from app.service.StockService import StockService
from app.model.dto import StockRunCrawling
from app.module.socket.manager import ConnectionManager
from uvicorn.config import logger
import uuid


REQ_SOCKET_STOCK_CRAWLING_MARCAP_STOCK_DATA = "stock/crawlingMarcapStockData"
REQ_SOCKET_STOCK_CANCEL_CRAWLING = "stock/cancelCrawling"


class StockSocketRouter(object):
    def __init__(self, stockService: StockService, manager: ConnectionManager) -> None:
        super().__init__()
        self.stockService = stockService
        self.manager = manager
        self.ee = manager.ee
        self.setupEvents()
    
    def setupEvents(self) -> None:
        self.ee.on("connect", self.connect)
        self.ee.on("message", self.message)
        self.ee.on(REQ_SOCKET_STOCK_CRAWLING_MARCAP_STOCK_DATA, self.crawlingMarcapStockData)
        self.ee.on(REQ_SOCKET_STOCK_CANCEL_CRAWLING, self.cancelCrawling)

    def connect(self, data: dict, websocket: WebSocket) -> None:
        print("connect")
    
    def message(self, data: dict, websocket: WebSocket) -> None:
        print(data)

    def crawlingMarcapStockData(self, data: dict, websocket: WebSocket) -> None:
        dtoList = []
        for market in data["market"]:
            taskUniqueId = data["taskId"]+market+data["startDate"]+data["endDate"]+str(uuid.uuid4())
            dto = StockRunCrawling(**{
                "driverAddr": "http://fin-carwling-webdriver:4444",
                "market": market,
                "startDateStr": data["startDate"],
                "endDateStr": data["endDate"],
                "taskId": data["taskId"],
                "taskUniqueId": taskUniqueId
            })
            dtoList.append(dto)
        self.stockService.crawlingMarcapStockData(dtoList)
    
    def cancelCrawling(self, data: dict, websocket: WebSocket) -> None:
        dtoList = []
        logger.info(str(data))
        for market in data["market"]:
            dto = StockRunCrawling(**{
                "driverAddr": "http://fin-carwling-webdriver:4444",
                "market": market,
                "startDateStr": data["startDate"],
                "endDateStr": data["endDate"],
                "taskId": data["taskId"],
                "taskUniqueId": data["taskUniqueId"]
            })
            dtoList.append(dto)
        for dto in dtoList:
            self.stockService.cancelCrawling(dto)
