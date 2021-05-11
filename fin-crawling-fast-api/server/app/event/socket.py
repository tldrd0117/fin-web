from fastapi import WebSocket
from app.model.model import StockCrawlingRunCrawling
from pymitter import EventEmitter
from app.event.manager import manager

ee = EventEmitter()


@ee.on("connect")
def connect(data: dict, websocket: WebSocket) -> None:
    print("connect")


@ee.on("message")
def message(data: dict, websocket: WebSocket) -> None:
    print(data)


@ee.on("crawling/checkDoingCrawling")
def checkDoingCrawling(data: dict, websocket: WebSocket) -> None:
    ee.emit("crawlingService/checkDoingCrawling")


@ee.on("crawling/runCrawling")
def runCrawling(data: dict, websocket: WebSocket) -> None:
    dto = StockCrawlingRunCrawling(**{
        "driverAddr": "http://webdriver:4444",
        "market": data["market"],
        "startDateStr": data["startDate"],
        "endDateStr": data["endDate"],
        "taskId": data["taskId"],
        "taskUniqueId": data["id"]
    })
    print(dto.dict())
    manager.send("fake", dto.dict(), websocket)
    # ee.emit("crawlingService/runCrawling", dto)


@ee.on("crawling/getTaskHistory")
def getTaskHistory(data: dict, websocket: WebSocket) -> None:
    print("getTaskHistory")
    print(data)
    ee.emit("crawlingService/getCompletedTask")


# @ee.on("crawling/updateTasks")
# def updateTasks(tasks: StockCrawlingTasksDTO) -> None:
#     socketio.emit("crawling/updateTasks", tasks.toDict(), broadcast=True)

# @ee.on("crawling/crawlingComplete")
# def crawlingComplete(data: StockCrawlingTaskDTO) -> None:
#     socketio.emit("crawling/crawlingComplete", data.toDict(), broadcast=True)

# @ee.on("crawling/crawlingStart")
# def crawlingStart(data: StockCrawlingTaskDTO) -> None:
#     socketio.emit("crawling/crawlingStart", data.toDict(), broadcast=True)

# @ee.on("crawling/updateTaskHistory")
# def updateTaskHistory(data: list, broadcast: bool = True) -> None:
#     socketio.emit("crawling/updateTaskHistory", data, broadcast=broadcast)