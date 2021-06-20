from fastapi import WebSocket
from app.model.model import StockCrawlingRunCrawling
from app.module.locator import Locator
from app.service.CrawlingService import CrawlingService
from app.event.manager import ConnectionManager
from uvicorn.config import logger

REQ_SOCKET_CRAWLING_FETCH_COMPLETED_TASK = "crawling/fetchCompletedTask"
REQ_SOCKET_CRAWLING_FETCH_TASKS = "crawling/fetchTasks"
REQ_SOCKET_CRAWLING_RUN_CRAWLING = "crawling/runCrawling"

manager: ConnectionManager = Locator.getInstance().get(ConnectionManager)
crawlingService: CrawlingService = Locator.getInstance().get(CrawlingService)


@manager.ee.on("connect")
def connect(data: dict, websocket: WebSocket) -> None:
    print("connect")


@manager.ee.on("message")
def message(data: dict, websocket: WebSocket) -> None:
    print(data)


@manager.ee.on(REQ_SOCKET_CRAWLING_FETCH_TASKS)
def fetchTasks(data: dict, websocket: WebSocket) -> None:
    print("fetchTasks!!")
    crawlingService.fetchTasks(websocket)


@manager.ee.on(REQ_SOCKET_CRAWLING_RUN_CRAWLING)
def runCrawling(data: dict, websocket: WebSocket) -> None:
    dto = StockCrawlingRunCrawling(**{
        "driverAddr": "http://webdriver:4444",
        "market": data["market"],
        "startDateStr": data["startDate"],
        "endDateStr": data["endDate"],
        "taskId": data["taskId"],
        "taskUniqueId": data["id"]
    })
    crawlingService.runCrawling(dto)


@manager.ee.on(REQ_SOCKET_CRAWLING_FETCH_COMPLETED_TASK)
def fetchCompletedTask(data: dict, websocket: WebSocket) -> None:
    crawlingService.fetchCompletedTask(websocket)
