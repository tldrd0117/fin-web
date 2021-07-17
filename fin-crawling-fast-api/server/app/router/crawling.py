from fastapi import WebSocket
from app.model.model import StockCrawlingRunCrawling
from app.service.CrawlingService import CrawlingService
from app.module.socket.manager import ConnectionManager
from uvicorn.config import logger
import uuid

REQ_SOCKET_CRAWLING_FETCH_COMPLETED_TASK = "crawling/fetchCompletedTask"
REQ_SOCKET_CRAWLING_FETCH_TASKS = "crawling/fetchTasks"
REQ_SOCKET_CRAWLING_RUN_CRAWLING = "crawling/runCrawling"


class CrawlingSocketRouter(object):
    def __init__(self, crawlingService: CrawlingService, manager: ConnectionManager) -> None:
        super().__init__()
        self.crawlingService = crawlingService
        self.manager = manager
        self.ee = manager.ee
        self.setupEvents()
    
    def setupEvents(self) -> None:
        self.ee.on("connect", self.connect)
        self.ee.on("message", self.message)
        self.ee.on(REQ_SOCKET_CRAWLING_FETCH_TASKS, self.fetchTasks)
        self.ee.on(REQ_SOCKET_CRAWLING_RUN_CRAWLING, self.runCrawling)
        self.ee.on(REQ_SOCKET_CRAWLING_FETCH_COMPLETED_TASK, self.fetchCompletedTask)

    def connect(self, data: dict, websocket: WebSocket) -> None:
        print("connect")

    def message(self, data: dict, websocket: WebSocket) -> None:
        print(data)

    def fetchTasks(self, data: dict, websocket: WebSocket) -> None:
        print("fetchTasks!!")
        logger.info("fetchTasks!!")
        self.crawlingService.fetchTasks(websocket)

    def runCrawling(self, data: dict, websocket: WebSocket) -> None:
        dtoList = []
        for market in data["market"]:
            taskUniqueId = data["taskId"]+market+data["startDate"]+data["endDate"]+str(uuid.uuid4())
            dto = StockCrawlingRunCrawling(**{
                "driverAddr": "http://webdriver:4444",
                "market": market,
                "startDateStr": data["startDate"],
                "endDateStr": data["endDate"],
                "taskId": data["taskId"],
                "taskUniqueId": taskUniqueId
            })
            dtoList.append(dto)
        self.crawlingService.runCrawling(dtoList)

    def fetchCompletedTask(self, data: dict, websocket: WebSocket) -> None:
        self.crawlingService.fetchCompletedTask(websocket)
