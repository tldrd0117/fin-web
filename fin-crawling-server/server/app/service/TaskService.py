
from app.module.logger import Logger
from typing import Any, List
from fastapi import WebSocket
from uvicorn.config import logger
import uuid


from app.service.FactorService import FactorService
from app.service.StockService import StockService
from app.model.dto import StockUpdateState, YearData, \
    StockTaskSchedule, StockTaskScheduleList, \
    StockTaskScheduleInfo, StockRunCrawling, \
    ProcessTasks, ListLimitData, RunFactorFileConvert, DartApiCrawling
from app.model.task import TaskPoolInfo
from app.module.locator import Locator
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.TasksRepository import TasksRepository, \
    EVENT_TASK_REPO_TASK_COMPLETE, EVENT_TASK_REPO_UPDATE_POOL_INFO, \
    EVENT_TASK_REPO_UPDATE_TASKS
from app.module.socket.manager import ConnectionManager
from app.util.DateUtils import getNowDateStr
from app.scheduler.TaskScheduler import TaskScheduler

RES_SOCKET_TASK_FETCH_TASKS = "task/progress/fetchTasksRes"
RES_SOCKET_TASK_FETCH_COMPLETED_TASK = "task/history/fetchCompletedTaskRes"
RES_SOCKET_TASK_FETCH_TASK_STATE = "task/calendar/fetchTaskStateRes"
RES_SOCKET_TASK_UPDATE_TASK_STATE = "task/calendar/updateTaskStateRes"
RES_SOCKET_TASK_FETCH_TASK_SCHEDULE = "task/schedule/fetchTaskScheduleRes"
RES_SOCKET_TASK_FETCH_TASK_POOL_INFO = "task/poolInfo/fetchTaskPoolInfoRes"


class TaskService:
    def __init__(
            self,
            manager: ConnectionManager,
            tasksRepository: TasksRepository,
            taskScheduler: TaskScheduler,
            factorService: FactorService,
            stockService: StockService,
            crawlerRepository: CrawlerRepository
            ) -> None:
        self.tasksRepository = tasksRepository
        self.crawlerRepository = crawlerRepository
        self.manager = manager
        self.taskScheduler = taskScheduler
        self.factorService = factorService
        self.stockService = stockService
        self.logger = Logger("TaskService")
        self.ee = self.tasksRepository.taskEventEmitter
        self.setupEvents()
    
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
            logger.info(f"jobargs: {str(jobs[i].args[0])}")
            stockTaskScheduleList.list.append(StockTaskScheduleInfo(**{
                "id": id,
                "year": str(fields[0]),
                "month": str(fields[1]),
                "day": str(fields[2]),
                "dayOfWeek": str(fields[4]),
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
    def marcapJob(marcapDtos: List[StockRunCrawling]) -> None:
        service: StockService = Locator.getInstance().get(StockService)
        for dto in marcapDtos:
            logger.info("#### schedule job start ####")
            logger.info("command" + dto.startDateStr + "~" + dto.endDateStr)
            dto.taskUniqueId = dto.taskId+dto.market+dto.startDateStr+dto.endDateStr+str(uuid.uuid4())
            if dto.startDateStr == "*" or dto.endDateStr == "*":
                dto.startDateStr = getNowDateStr()
                dto.endDateStr = getNowDateStr()
            logger.info("real:" + dto.startDateStr + "~" + dto.endDateStr)
        service.crawlingMarcapStockData(marcapDtos)
    
    def addTaskSchedule(self, scheduleDto: StockTaskSchedule, runCrawlingDto: List[StockRunCrawling], webSocket: WebSocket) -> None:
        marcapDtos = []
        for dto in runCrawlingDto:
            if dto.taskId == "marcap":
                marcapDtos.append(dto)
        
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
            args=[marcapDtos])
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

    def updateTaskState(self, taskId: str, stockUpdateState: StockUpdateState = None) -> None:
        if stockUpdateState is not None:
            self.manager.sendBroadCast(RES_SOCKET_TASK_UPDATE_TASK_STATE, stockUpdateState.dict())
        self.fetchTasks()

    def getTaskPoolInfo(self, webSocket: WebSocket) -> None:
        taskPoolInfo: TaskPoolInfo = self.tasksRepository.getPoolInfo()
        self.manager.send(RES_SOCKET_TASK_FETCH_TASK_POOL_INFO, taskPoolInfo.dict(), webSocket)
    
    def updateTaskPoolInfo(self, poolInfo: TaskPoolInfo) -> None:
        # logger.info(f"updateTaskPoolInfo:{poolInfo.json()}")
        self.manager.sendBroadCast(RES_SOCKET_TASK_FETCH_TASK_POOL_INFO, poolInfo.dict())
    
    def addTask(self, taskName: str, dto: Any) -> None:
        if isinstance(dto, dict):
            if taskName == "crawlingMarcapStockData":
                data = []
                for market in dto["market"]:
                    taskUniqueId = dto["taskId"]+market+dto["startDate"]+dto["endDate"]+str(uuid.uuid4())
                    dtoOne = StockRunCrawling(**{
                        "driverAddr": "http://fin-carwling-webdriver:4444",
                        "market": market,
                        "startDateStr": dto["startDate"],
                        "endDateStr": dto["endDate"],
                        "taskId": dto["taskId"],
                        "taskUniqueId": taskUniqueId
                    })
                    data.append(dtoOne)
            elif taskName == "convertFactorFileToDb":
                data = RunFactorFileConvert(**{
                    "taskId": dto["taskId"],
                    "taskUniqueId": dto["taskId"] + str(uuid.uuid4())
                })
            elif taskName == "crawlingFactorDartData":
                data = DartApiCrawling(**{
                    "apiKey": dto["apiKey"],
                    "isCodeNew": dto["isCodeNew"],
                    "startYear": dto["startYear"],
                    "endYear": dto["endYear"],
                    "taskId": dto["taskId"],
                    "taskUniqueId": dto["taskId"] + dto["startYear"] + dto["endYear"] + str(uuid.uuid4())
                })
        else:
            data = dto
        if taskName == "convertFactorFileToDb":
            self.factorService.convertFactorFileToDb(data)
        elif taskName == "crawlingMarcapStockData":
            self.stockService.crawlingMarcapStockData(data)
        elif taskName == "crawlingFactorDartData":
            self.factorService.crawlingFactorDartData(data)
    
    def cancelTask(self, taskId: str, taskUniqueId: str) -> None:
        if taskId == "marcap":
            if taskUniqueId in self.crawlerRepository.getCrawlers():
                self.tasksRepository.taskRunner.cancel(taskUniqueId)
                self.crawlerRepository.getCrawlers(taskUniqueId).isCancelled = True
            else:
                task = self.tasksRepository.getTask(taskId, taskUniqueId)
                if task is not None:
                    self.tasksRepository.deleteTask(task)
        else:
            self.tasksRepository.taskRunner.cancel(taskUniqueId)
            task = self.tasksRepository.getTask(taskId, taskUniqueId)
            if task is not None:
                self.tasksRepository.deleteTask(task)
    
    def fetchCompletedTask(self, dto: ListLimitData, webSocket: WebSocket) -> None:
        tasks = self.tasksRepository.getCompletedTask(dto)
        self.manager.send(RES_SOCKET_TASK_FETCH_COMPLETED_TASK, tasks.dict(), webSocket)
        

    
