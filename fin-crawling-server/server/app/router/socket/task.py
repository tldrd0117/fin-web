
import asyncio
from fastapi import WebSocket
from app.model.dto import StockRunCrawling, StockTaskSchedule, ListLimitData
from app.service.api.TaskApiService import TaskApiService
from app.module.socket.manager import ConnectionManager
from app.base.BaseComponent import BaseComponent
from pymitter import EventEmitter
from app.util.decorator import eventsDecorator as ed


class TaskSocketRouter(BaseComponent):

    def onComponentResisted(self) -> None:
        self.taskApiService = self.get(TaskApiService)
        self.manager = self.get(ConnectionManager)
        self.ee: EventEmitter = self.manager.ee
        ed.register(self, self.ee)
        return super().onComponentResisted()
    
    
    @ed.on("task/progress/fetchTasks")
    async def fetchTasks(self, data: dict, websocket: WebSocket) -> None:
        self.taskApiService.fetchTasks(websocket=websocket)

    @ed.on("task/calendar/fetchTaskState")
    async def fetchTaskState(self, data: dict, websocket: WebSocket) -> None:
        self.taskApiService.getTaskState(data["taskId"], websocket)
    
    @ed.on("task/poolInfo/fetchTaskPoolInfo")
    async def fetchTaskPoolInfo(self, data: dict, websocket: WebSocket) -> None:
        self.taskApiService.getTaskPoolInfo(websocket)

    @ed.on("task/schedule/fetchTaskSchedule")
    async def fetchTaskSchedule(self, data: dict, websocket: WebSocket) -> None:
        self.taskApiService.getTaskSchedule(websocket)
    
    @ed.on("task/progress/addTask")
    async def addTask(self, data: dict, websocket: WebSocket) -> None:
        asyncio.create_task(self.taskApiService.addTask(data["taskName"], data))

    @ed.on("task/schedule/addTaskSchedule")
    async def addTaskSchedule(self, data: dict, websocket: WebSocket) -> None:
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

        self.taskApiService.addTaskSchedule(data["taskName"], scheduleDto, data, websocket)

    @ed.on("task/schedule/removeTaskSchedule")
    async def removeTaskSchedule(self, data: dict, websocket: WebSocket) -> None:
        self.taskApiService.removeTaskSchedule(data["id"], websocket)

    @ed.on("task/history/fetchCompletedTask")
    async def fetchCompletedTask(self, data: dict, websocket: WebSocket) -> None:
        dto = ListLimitData(**{
            "offset": data["offset"],
            "limit": data["limit"],
            "taskId": data["taskId"]
        })
        self.taskApiService.fetchCompletedTask(dto, websocket)
    
    @ed.on("task/progress/cancelTask")
    async def cancelTask(self, data: dict, websocket: WebSocket) -> None:
        self.taskApiService.cancelTask(data["taskId"], data["taskUniqueId"])