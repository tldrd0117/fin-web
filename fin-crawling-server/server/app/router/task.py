
from fastapi import WebSocket
from app.model.dto import StockRunCrawling, StockTaskSchedule
from app.service.CrawlingService import CrawlingService
from app.service.TaskService import TaskService
from app.module.socket.manager import ConnectionManager

REQ_SOCKET_TASK_FETCH_TASK_STATE = "task/fetchTaskState"
REQ_SOCKET_TASK_FETCH_TASK_POOL_INFO = "task/fetchTaskPoolInfo"
REQ_SOCKET_TASK_FETCH_TASK_SCHEDULE = "taskSchedule/fetchTaskSchedule"
REQ_SOCKET_TASK_ADD_TASK_SCHEDULE = "taskSchedule/addTaskSchedule"
REQ_SOCKET_TASK_REMOVE_TASK_SCHEDULE = "taskSchedule/removeTaskSchedule"


class TaskSocketRouter(object):
    def __init__(self, crawlingService: CrawlingService, taskService: TaskService, manager: ConnectionManager) -> None:
        super().__init__()
        self.crawlingService = crawlingService
        self.taskService = taskService
        self.manager = manager
        self.ee = self.manager.ee
        self.setupEvents()
    
    def setupEvents(self) -> None:
        self.ee.on(REQ_SOCKET_TASK_FETCH_TASK_STATE, self.fetchTaskState)
        self.ee.on(REQ_SOCKET_TASK_FETCH_TASK_SCHEDULE, self.fetchTaskSchedule)
        self.ee.on(REQ_SOCKET_TASK_ADD_TASK_SCHEDULE, self.addTaskSchedule)
        self.ee.on(REQ_SOCKET_TASK_REMOVE_TASK_SCHEDULE, self.removeTaskSchedule)

    def fetchTaskState(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.getTaskState(data["taskId"], websocket)
    
    def fetchTaskPoolInfo(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.getTaskPoolInfo(websocket)

    def fetchTaskSchedule(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.getTaskSchedule(websocket)

    def addTaskSchedule(self, data: dict, websocket: WebSocket) -> None:
        # if data["startDate"] == "*":
        #     data["startDate"] = getNowDateStr()
        #     data["endDate"] = getNowDateStr()

        scheduleDto = StockTaskSchedule(**{
            "year": data["year"],
            "month": data["month"],
            "dayOfWeek": data["dayOfWeek"],
            "day": data["day"],
            "hour": data["hour"],
            "minute": data["minute"],
            "second": data["second"]
        })

        dtoList = []
        for market in data["market"]:
            dto = StockRunCrawling(**{
                "driverAddr": "http://fin-carwling-webdriver:4444",
                "market": market,
                "startDateStr": data["startDate"],
                "endDateStr": data["endDate"],
                "taskId": data["taskId"],
                "taskUniqueId": ""
            })
            dtoList.append(dto)
        self.taskService.addTaskSchedule(scheduleDto, dtoList, websocket)

    def removeTaskSchedule(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.removeTaskSchedule(data["id"], websocket)
