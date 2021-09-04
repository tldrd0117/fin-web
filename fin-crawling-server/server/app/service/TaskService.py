
from typing import List
from app.model.dto import StockCrawlingRunCrawling, StockTaskSchedule, StockTaskScheduleList, StockTaskState, StockTaskScheduleInfo
from app.model.task import TaskPoolInfo
from app.module.locator import Locator
from app.repo.TasksRepository import TasksRepository, EVENT_TASK_REPO_TASK_COMPLETE, EVENT_TASK_REPO_UPDATE_POOL_INFO
from app.module.socket.manager import ConnectionManager
from app.util.DateUtils import getNowDateStr
from app.scheduler.TaskScheduler import TaskScheduler
from fastapi import WebSocket

from app.service.CrawlingService import CrawlingService
from uvicorn.config import logger

RES_SOCKET_TASK_FETCH_TASK_STATE = "task/fetchTaskStateRes"
RES_SOCKET_TASK_FETCH_TASK_SCHEDULE = "taskSchedule/fetchTaskScheduleRes"
RES_SOCKET_TASK_FETCH_TASK_POOL_INFO = "task/fetchTaskPoolInfoRes"


class TaskService:
    def __init__(
            self,
            manager: ConnectionManager,
            tasksRepository: TasksRepository,
            taskScheduler: TaskScheduler,
            crawlingService: CrawlingService
            ) -> None:
        self.tasksRepository = tasksRepository
        self.manager = manager
        self.taskScheduler = taskScheduler
        self.crawlingService = crawlingService
        self.ee = self.tasksRepository.taskEventEmitter
        self.setupEvents()
    
    def setupEvents(self) -> None:
        self.ee.on(EVENT_TASK_REPO_TASK_COMPLETE, self.updateTaskState)
        self.ee.on(EVENT_TASK_REPO_UPDATE_POOL_INFO, self.updateTaskPoolInfo)
    
    def getTaskSchedule(self, webSocket: WebSocket, isBroadCast: bool = False) -> None:
        jobs = self.taskScheduler.getJobs()
        stockTaskScheduleList = StockTaskScheduleList(**{"list": []})
        for i in range(len(jobs)):
            fields = jobs[i].trigger.fields
            id = jobs[i].id
            logger.info(f"jobargs: {str(jobs[i].args[0])}")
            stockTaskScheduleList.list.append(StockTaskScheduleInfo(**{
                "id": id,
                "year": str(fields[0]),
                "month": str(fields[1]),
                "day": str(fields[2]),
                "hour": str(fields[5]),
                "minute": str(fields[6]),
                "second": str(fields[7]),
                "taskList": list(jobs[i].args[0])
            }))
        if isBroadCast:
            self.manager.sendBroadCast(RES_SOCKET_TASK_FETCH_TASK_SCHEDULE, stockTaskScheduleList.dict())
        else:
            self.manager.send(RES_SOCKET_TASK_FETCH_TASK_SCHEDULE, stockTaskScheduleList.dict(), webSocket)
    
    @staticmethod
    def marcapJob(marcapDtos: List[StockCrawlingRunCrawling]) -> None:
        service: CrawlingService = Locator.getInstance().get(CrawlingService)
        for dto in marcapDtos:
            logger.info("#### schedule job start ####")
            logger.info("command" + dto.startDateStr + "~" + dto.endDateStr)
            if dto.startDateStr == "*" or dto.endDateStr == "*":
                dto.startDateStr = getNowDateStr()
                dto.endDateStr = getNowDateStr()
            logger.info("real:" + dto.startDateStr + "~" + dto.endDateStr)
        service.runCrawling(marcapDtos)
    
    def addTaskSchedule(self, scheduleDto: StockTaskSchedule, runCrawlingDto: List[StockCrawlingRunCrawling], webSocket: WebSocket) -> None:
        marcapDtos = []
        for dto in runCrawlingDto:
            if dto.taskId == "marcap":
                marcapDtos.append(dto)
        
        self.taskScheduler.addJob(
            self.marcapJob, 
            scheduleDto.year, 
            scheduleDto.month, 
            scheduleDto.day, 
            scheduleDto.hour, 
            scheduleDto.minute, 
            scheduleDto.second, 
            "marcap",
            args=[marcapDtos])
        self.getTaskSchedule(webSocket, True)
        
    def removeTaskSchedule(self, id: str, webSocket: WebSocket) -> None:
        self.taskScheduler.removeJob(id)
        self.getTaskSchedule(webSocket, True)
        
    def getTaskState(self, taskId: str, webSocket: WebSocket) -> None:
        data: StockTaskState = self.tasksRepository.getAllTaskState(taskId)
        self.manager.send(RES_SOCKET_TASK_FETCH_TASK_STATE, data.dict(), webSocket)

    def updateTaskState(self, taskId: str) -> None:
        data: StockTaskState = self.tasksRepository.getAllTaskState(taskId)
        self.manager.sendBroadCast(RES_SOCKET_TASK_FETCH_TASK_STATE, data.dict())

    def getTaskPoolInfo(self, webSocket: WebSocket) -> None:
        taskPoolInfo: TaskPoolInfo = self.tasksRepository.getPoolInfo()
        self.manager.send(RES_SOCKET_TASK_FETCH_TASK_POOL_INFO, taskPoolInfo.dict(), webSocket)
    
    def updateTaskPoolInfo(self, poolInfo: TaskPoolInfo) -> None:
        # logger.info(f"updateTaskPoolInfo:{poolInfo.json()}")
        self.manager.sendBroadCast(RES_SOCKET_TASK_FETCH_TASK_POOL_INFO, poolInfo.dict())
