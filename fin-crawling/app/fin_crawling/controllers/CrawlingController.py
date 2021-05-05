from flask_socketio import SocketIO

from fin_crawling.data.StockCrawlingRunCrawlingDTO import \
    StockCrawlingRunCrawlingDTO
from fin_crawling.data.StockCrawlingTaskDTO import StockCrawlingTaskDTO
from fin_crawling.data.StockCrawlingTasksDTO import StockCrawlingTasksDTO
from fin_crawling.service.CrawlingService import setupCrawlingService
from fin_crawling.utils.EventEmitterWrapper import ee

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
# from fin_crawling.app import socketio


def setupCrawlingController(socketio: SocketIO) -> None:
    setupCrawlingService()

    @socketio.on("connect")
    def connect() -> None:
        print("connect")

    @socketio.on("message")
    def message(data: dict) -> None:
        print(data)

    @socketio.on("crawling/checkDoingCrawling")
    def checkDoingCrawling() -> None:
        ee.emit("crawlingService/checkDoingCrawling")

    @socketio.on("crawling/runCrawling")
    def runCrawling(data: dict) -> None:
        dto = StockCrawlingRunCrawlingDTO.create(
            driverAddr="http://webdriver:4444",
            market=data["market"],
            startDateStr=data["startDate"],
            endDateStr=data["endDate"],
            taskId=data["taskId"],
            taskUniqueId=data["id"])
        ee.emit("crawlingService/runCrawling", dto)

    @socketio.on("crawling/getTaskHistory")
    def getTaskHistory(data: dict) -> None:
        print("getTaskHistory")
        print(data)
        ee.emit("crawlingService/getCompletedTask")

    @ee.on("crawling/updateTasks")
    def updateTasks(tasks: StockCrawlingTasksDTO) -> None:
        socketio.emit("crawling/updateTasks", tasks.toDict(), broadcast=True)

    @ee.on("crawling/crawlingComplete")
    def crawlingComplete(data: StockCrawlingTaskDTO) -> None:
        socketio.emit("crawling/crawlingComplete", data.toDict(), broadcast=True)

    @ee.on("crawling/crawlingStart")
    def crawlingStart(data: StockCrawlingTaskDTO) -> None:
        socketio.emit("crawling/crawlingStart", data.toDict(), broadcast=True)

    @ee.on("crawling/updateTaskHistory")
    def updateTaskHistory(data: list, broadcast: bool = True) -> None:
        socketio.emit("crawling/updateTaskHistory", data, broadcast=broadcast)
