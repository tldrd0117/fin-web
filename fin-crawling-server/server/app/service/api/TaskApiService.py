
import asyncio
from app.module.logger import Logger
from typing import Any, Callable, Dict, List
from fastapi import WebSocket
import uuid

from app.service.scrap.FactorDartScrapService import FactorDartScrapService
from app.service.scrap.FactorFileScrapService import FactorFileScrapService
from app.service.scrap.MarcapScrapService import MarcapScrapService
from app.service.scrap.SeibroDividendScrapService import SeibroDividendScrapService
from app.service.scrap.SeibroStockNumScrapService import SeibroStockNumScrapService
from app.model.dto import StockUpdateState, YearData, \
    StockTaskSchedule, StockTaskScheduleList, \
    StockTaskScheduleInfo, StockRunCrawling, \
    ProcessTasks, ListLimitData, ProcessTask
from app.model.scrap.model import MarcapRunScrap
from app.model.task.model import TaskPoolInfo
from app.model.dao import ListLimitDao
from app.module.locator import Locator

from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import TasksRepository, \
    EVENT_TASK_REPO_TASK_COMPLETE, EVENT_TASK_REPO_UPDATE_POOL_INFO, \
    EVENT_TASK_REPO_UPDATE_TASKS
from app.module.socket.manager import ConnectionManager
from app.scheduler.TaskScheduler import TaskScheduler
from app.base.BaseComponent import BaseComponent
from app.service.base.TaskService import TaskService

RES_SOCKET_TASK_FETCH_TASKS = "task/progress/fetchTasksRes"
RES_SOCKET_TASK_FETCH_COMPLETED_TASK = "task/history/fetchCompletedTaskRes"
RES_SOCKET_TASK_FETCH_TASK_STATE = "task/calendar/fetchTaskStateRes"
RES_SOCKET_TASK_UPDATE_TASK_STATE = "task/calendar/updateTaskStateRes"
RES_SOCKET_TASK_FETCH_TASK_SCHEDULE = "task/schedule/fetchTaskScheduleRes"
RES_SOCKET_TASK_FETCH_TASK_POOL_INFO = "task/poolInfo/fetchTaskPoolInfoRes"


class TaskApiService(BaseComponent):
        
    def onComponentResisted(self) -> None:
        self.tasksRepository = self.get(TasksRepository)
        self.crawlerRepository = self.get(CrawlerRepository)
        self.manager = self.get(ConnectionManager)
        self.taskScheduler = self.get(TaskScheduler)
        self.taskApiService = self.get(TaskApiService)
        self.taskServices = {
            "MarcapScrapService": self.get(MarcapScrapService),
            "FactorDartScrapService": self.get(FactorDartScrapService),
            "FactorFileScrapService": self.get(FactorFileScrapService),
            "SeibroDividendScrapService": self.get(SeibroDividendScrapService),
            "SeibroStockNumScrapService": self.get(SeibroStockNumScrapService)
        }

        self.logger = Logger("TaskService")
        self.ee = self.tasksRepository.ee
        self.setupEvents()
        return super().onComponentResisted()
    
    def setupEvents(self) -> None:
        self.ee.on(EVENT_TASK_REPO_UPDATE_TASKS, self.fetchTasks)
        self.ee.on(EVENT_TASK_REPO_TASK_COMPLETE, self.updateTaskState)
        self.ee.on(EVENT_TASK_REPO_UPDATE_POOL_INFO, self.updateTaskPoolInfo)
    
    def getTaskSchedule(self, webSocket: WebSocket, isBroadCast: bool = False) -> None:
        jobs = self.taskScheduler.getJobs()
        stockTaskScheduleList = StockTaskScheduleList(**{"list": []})
        for i in range(len(jobs)):
            fields = jobs[i].trigger.fields
            id = jobs[i].id
            self.logger.info(f"jobargs: {str(jobs[i].args[0])}")
            stockTaskScheduleList.list.append(StockTaskScheduleInfo(**{
                "id": id,
                "year": str(fields[0]),
                "month": str(fields[1]),
                "day": str(fields[2]),
                "dayOfWeek": str(fields[4]),
                "hour": str(fields[5]),
                "minute": str(fields[6]),
                "second": str(fields[7]),
                # 변경필요 "taskList": list(jobs[i].args[1])
            }))
        if isBroadCast:
            self.manager.sendBroadCast(RES_SOCKET_TASK_FETCH_TASK_SCHEDULE, stockTaskScheduleList.dict())
        else:
            self.manager.send(RES_SOCKET_TASK_FETCH_TASK_SCHEDULE, stockTaskScheduleList.dict(), webSocket)
    
    @staticmethod
    def marcapJob(taskName:str, dto: dict) -> None:
        service: TaskApiService = Locator.getInstance().get(TaskApiService)
        logger = Logger("TaskService_marcapJob")
        logger.info(f"taskName:{taskName} dtos:{str(dto)}")
        asyncio.run(service.addTask(taskName, dto))
        
    
    def addTaskSchedule(self, taskName: str, scheduleDto: StockTaskSchedule, dto: List[MarcapRunScrap], webSocket: WebSocket) -> None:
        
        self.taskScheduler.addJob(
            self.marcapJob, 
            scheduleDto.year, 
            scheduleDto.month, 
            scheduleDto.dayOfWeek,
            scheduleDto.day, 
            scheduleDto.hour, 
            scheduleDto.minute, 
            scheduleDto.second, 
            "marcap",
            args=[taskName, dto])
        self.getTaskSchedule(webSocket, True)
        
    def removeTaskSchedule(self, id: str, webSocket: WebSocket) -> None:
        self.taskScheduler.removeJob(id)
        self.getTaskSchedule(webSocket, True)
    
    def fetchTasks(self, data: ProcessTasks = None, websocket: WebSocket = None) -> None:
        if data is None:
            data = self.tasksRepository.tasksdto
        self.logger.info("fetchTasks", data.json())
        if websocket is None:
            self.manager.sendBroadCast(RES_SOCKET_TASK_FETCH_TASKS, data.dict())
        else:
            self.manager.send(RES_SOCKET_TASK_FETCH_TASKS, data.dict(), websocket)
        
    def getTaskState(self, taskId: str, webSocket: WebSocket) -> None:
        data: YearData = self.tasksRepository.getAllTaskState(taskId)
        self.manager.send(RES_SOCKET_TASK_FETCH_TASK_STATE, data.dict(), webSocket)

    def updateTaskState(self, stockUpdateState: StockUpdateState = None) -> None:
        if stockUpdateState is not None:
            self.manager.sendBroadCast(RES_SOCKET_TASK_UPDATE_TASK_STATE, stockUpdateState.dict())
        self.fetchTasks()

    def getTaskPoolInfo(self, webSocket: WebSocket) -> None:
        taskPoolInfo: TaskPoolInfo = self.tasksRepository.getPoolInfo()
        self.manager.send(RES_SOCKET_TASK_FETCH_TASK_POOL_INFO, taskPoolInfo.dict(), webSocket)
    
    def updateTaskPoolInfo(self, poolInfo: TaskPoolInfo) -> None:
        # logger.info(f"updateTaskPoolInfo:{poolInfo.json()}")
        self.manager.sendBroadCast(RES_SOCKET_TASK_FETCH_TASK_POOL_INFO, poolInfo.dict())
    
    async def addTask(self, taskName: str, dto: Dict) -> None:
        # data = dto
        print(taskName)
        if taskName in self.taskServices:
            taskFunc: TaskService = self.taskServices[taskName]
            if taskFunc is not None:
                await asyncio.create_task(taskFunc.addTask(dto))
        else:
            self.logger.error("addTask", "not exist service")
        # if taskName == "convertFactorFileToDb":
        #     asyncio.create_task(self.factorFileScrapService.addCrawlingTask(dto))
        # elif taskName == "crawlingMarcapStockData":
        #     asyncio.create_task(self.marcapScrapService.addCrawlingTasks(dto))
        # elif taskName == "crawlingFactorDartData":
        #     asyncio.create_task(self.factorDartScrapService.addCrawlingTask(dto))
    
    
    def cancelTask(self, taskId: str, taskUniqueId: str) -> None:
        if taskUniqueId in self.crawlerRepository.getCrawlers():
            self.crawlerRepository.getCrawler(taskUniqueId).isCancelled = True
        self.tasksRepository.taskRunner.cancel(taskUniqueId)
        task: ProcessTask = self.tasksRepository.getTask(taskId, taskUniqueId)
        if task is not None:
            if task.state == "cancel":
                self.tasksRepository.deleteTask(task)
                self.tasksRepository.updateAllTask()
            elif task.state == "error":
                self.tasksRepository.deleteTask(task)
                self.tasksRepository.updateAllTask()
            else:
                task.state = "cancel"
                self.tasksRepository.updateTask(task)
        else:
            self.tasksRepository.updateAllTask()
    
    def fetchCompletedTask(self, dto: ListLimitData, webSocket: WebSocket) -> None:
        dao = ListLimitDao(**{
            "limit": dto.limit,
            "offset": dto.offset,
            "taskId": dto.taskId
        })
        tasks = self.tasksRepository.getCompletedTask(dao)
        self.manager.send(RES_SOCKET_TASK_FETCH_COMPLETED_TASK, tasks.dict(), webSocket)
        

    
