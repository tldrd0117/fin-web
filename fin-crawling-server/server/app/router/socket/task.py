
from fastapi import WebSocket
from app.model.dto import StockRunCrawling, StockTaskSchedule, ListLimitData
from app.service.TaskService import TaskService
from app.module.socket.manager import ConnectionManager

REQ_SOCKET_TASK_FETCH_TASK_STATE = "task/calendar/fetchTaskState"
REQ_SOCKET_TASK_FETCH_TASK_POOL_INFO = "task/poolInfo/fetchTaskPoolInfo"
REQ_SOCKET_TASK_FETCH_TASK_SCHEDULE = "task/schedule/fetchTaskSchedule"
REQ_SOCKET_TASK_ADD_TASK_SCHEDULE = "task/schedule/addTaskSchedule"
REQ_SOCKET_TASK_REMOVE_TASK_SCHEDULE = "task/schedule/removeTaskSchedule"
REQ_SOCKET_TASK_ADD_TASK = "task/progress/addTask"
REQ_SOCKET_TASK_FETCH_TASKS = "task/progress/fetchTasks"
REQ_SOCKET_TASK_CANCEL_TASK = "task/progress/cancelTask"
REQ_SOCKET_TASK_FETCH_COMPLETED_TASK = "task/history/fetchCompletedTask"


class TaskSocketRouter(object):
    def __init__(self, taskService: TaskService, manager: ConnectionManager) -> None:
        super().__init__()
        self.taskService = taskService
        self.manager = manager
        self.ee = self.manager.ee
        self.setupEvents()
    
    def setupEvents(self) -> None:
        self.ee.on(REQ_SOCKET_TASK_FETCH_TASK_STATE, self.fetchTaskState)
        self.ee.on(REQ_SOCKET_TASK_FETCH_TASK_SCHEDULE, self.fetchTaskSchedule)
        self.ee.on(REQ_SOCKET_TASK_ADD_TASK_SCHEDULE, self.addTaskSchedule)
        self.ee.on(REQ_SOCKET_TASK_REMOVE_TASK_SCHEDULE, self.removeTaskSchedule)
        self.ee.on(REQ_SOCKET_TASK_ADD_TASK, self.addTask)
        self.ee.on(REQ_SOCKET_TASK_FETCH_TASKS, self.fetchTasks)
        self.ee.on(REQ_SOCKET_TASK_FETCH_COMPLETED_TASK, self.fetchCompletedTask)
        self.ee.on(REQ_SOCKET_TASK_CANCEL_TASK, self.cancelTask)
    
    def fetchTasks(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.fetchTasks(websocket=websocket)

    def fetchTaskState(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.getTaskState(data["taskId"], websocket)
    
    def fetchTaskPoolInfo(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.getTaskPoolInfo(websocket)

    def fetchTaskSchedule(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.getTaskSchedule(websocket)
    
    def addTask(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.addTask(data["taskName"], data)

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

    def fetchCompletedTask(self, data: dict, websocket: WebSocket) -> None:
        dto = ListLimitData(**{
            "offset": data["offset"],
            "limit": data["limit"],
            "taskId": data["taskId"]
        })
        self.taskService.fetchCompletedTask(dto, websocket)
    
    def cancelTask(self, data: dict, websocket: WebSocket) -> None:
        self.taskService.cancelTask(data["taskId"], data["taskUniqueId"])