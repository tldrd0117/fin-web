from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Final, Optional

from pymitter import EventEmitter
from app.crawler.MarcapCrawler import EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, \
    EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_START_CRAWLING
from app.datasource.StockMongoDataSource import mongod
from app.model.dto import StockCrawlingCompletedTasksDTO, StockCrawlingDownloadTaskDTO, StockCrawlingRunCrawlingDTO, StockCrawlingTasksDTO, StockMarketCapitalResultDTO, StockCrawlingTaskDTO
from app.module.task import Task, TaskRunner


from uvicorn.config import logger

SUCCESS: Final = 1
FAIL: Final = 2
WAIT: Final = 0

EVENT_TASK_REPO_UPDATE_TASKS = "taskRepo/updateTasks"
EVENT_TASK_REPO_TASK_COMPLETE = "taskRepo/completeTask"


class TasksRepository(object):
    def __init__(self) -> None:
        super().__init__()
        self.taskEventEmitter = EventEmitter()
        self.tasksdto = StockCrawlingTasksDTO()
        self.taskRunner: Optional[TaskRunner] = None
        self.createTaskRunner()
    
    def createTaskRunner(self) -> None:
        if self.taskRunner is None:
            self.taskRunner = TaskRunner()
            self.taskRunner.run()

    def runTask(self, task: Task) -> None:
        print("runTask")
        if self.taskRunner:
            self.taskRunner.put(task)
    
    def runMarcapTask(self, workerTask: Task, dto: StockCrawlingRunCrawlingDTO) -> None:
        if self.taskRunner:
            startDate = datetime.strptime(dto.startDateStr, "%Y%m%d")
            endDate = datetime.strptime(dto.endDateStr, "%Y%m%d")
            taskDates = [(startDate + timedelta(days=x)).strftime("%Y%m%d") for x in range((endDate - startDate).days + 1)]
            task = StockCrawlingTaskDTO(**{
                "market": dto.market,
                "startDateStr": dto.startDateStr,
                "endDateStr": dto.endDateStr,
                "taskUniqueId": dto.taskUniqueId,
                "taskId": dto.taskId,
                "count": len(taskDates),
                "tasks": deque(taskDates),
                "restCount": len(taskDates),
                "tasksRet": deque(([0]*len(taskDates))),
            })
            task.state = "find worker"
            self.addTask(task)
            self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
            self.runTask(workerTask)

    def addTask(self, task: StockCrawlingTaskDTO) -> None:
        if "marcap" not in self.tasksdto.tasks:
            self.tasksdto.tasks[task.taskId] = dict()
            self.tasksdto.tasks[task.taskId]["list"] = dict()
            self.tasksdto.tasks[task.taskId]["ids"] = []
            self.tasksdto.taskIds.append("marcap")
        self.tasksdto.tasks[task.taskId]["list"][task.taskUniqueId] = task
        self.tasksdto.tasks[task.taskId]["ids"].append(task.taskUniqueId)

    def updateTask(self, task: StockCrawlingTaskDTO) -> None:
        self.tasksdto.tasks[task.taskId]["list"][task.taskUniqueId] = task
    
    def getTask(self, taskId: str, taskUniqueId: str) -> StockCrawlingTaskDTO:
        return self.tasksdto.tasks[taskId]["list"][taskUniqueId]

    def deleteTask(self, task: StockCrawlingTaskDTO) -> None:
        del self.tasksdto.tasks[task.taskId]["list"][task.taskUniqueId]
        self.tasksdto.tasks[task.taskId]["ids"].remove(task.taskUniqueId)
    
    def success(self, task: StockCrawlingTaskDTO, count: int) -> None:
        task.successCount = task.successCount + count
        task.restCount = task.restCount - count
        i = 0
        for _ in range(count):
            task.tasksRet[task.index + i] = SUCCESS
            i = i+1
        task.index = task.index + count
        task.percent = (task.successCount+task.failCount)/task.count * 100
        if task.restCount <= 0:
            task.state = "success"
        else:
            task.state = "waiting next task"

    def fail(self, task: StockCrawlingTaskDTO, count: int) -> None:
        task.failCount = task.failCount + count
        task.restCount = task.restCount - count
        i = 0
        for _ in range(count):
            logger.info("count:"+str(count))
            logger.info("index:"+str(task.index))
            logger.info("i:"+str(i))
            logger.info("_:"+str(_))
            left = task.tasks[task.index + i]
            task.failTasks.append(left)
            task.tasksRet[task.index + i] = FAIL
            i = i+1
        task.index = task.index + count
        task.percent = (task.successCount+task.failCount)/task.count * 100
        if task.restCount <= 0:
            task.state = "fail"
        else:
            task.state = "waiting next task"
    
    def getCompletedTask(self) -> StockCrawlingCompletedTasksDTO:
        taskData = mongod.getCompletedTask()
        logger.info("taskData:"+str(taskData))
        tasks: Dict = dict()
        taskIds = []
        for task in taskData:
            logger.info("task:"+str(task))
            logger.info("taskId:"+str(task["taskId"]))
            logger.info("tasks:"+str(tasks))
            if task["taskId"] not in tasks:
                tasks[task["taskId"]] = dict()
                tasks[task["taskId"]]["list"] = dict()
                tasks[task["taskId"]]["ids"] = []
                taskIds.append(task["taskId"])
            tasks[task["taskId"]]["list"][task["taskUniqueId"]] = task
            tasks[task["taskId"]]["ids"].append(task["taskUniqueId"])
            
        stockCrawlingCompletedTasksDTO = StockCrawlingCompletedTasksDTO(**{
            "history": tasks,
            "historyIds": taskIds
        })
        logger.info(stockCrawlingCompletedTasksDTO.json())
        return stockCrawlingCompletedTasksDTO

    def createListners(self, ee: EventEmitter) -> None:
        ee.on(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, self.onConnectingWebDriver)
        ee.on(EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, self.onStartCrawling)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, self.onDownloadStart)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, self.onDownloadComplete)
        ee.on(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, self.onParsingComplete)
    
    def onConnectingWebDriver(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "connecting webdriver"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        mongod.upsertTask(task.dict())

    def onStartCrawling(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "start crawling"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        mongod.upsertTask(task.dict())
    
    def onDownloadStart(self, dto: StockCrawlingDownloadTaskDTO) -> None:
        logger.info("onDownloadStart: "+dto.json())
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download start"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        mongod.upsertTask(task.dict())

    def onDownloadComplete(self, dto: StockCrawlingDownloadTaskDTO) -> None:
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download complete"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        mongod.upsertTask(task.dict())

    def onParsingComplete(self, isSuccess: bool, retdto: StockMarketCapitalResultDTO, dto: StockCrawlingDownloadTaskDTO) -> None:
        logger.info("onParsingComplete")
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        if isSuccess:
            self.success(task, 1)
        else:
            self.fail(task, 1)
        if task.restCount <= 0:
            self.deleteTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        mongod.upsertTask(task.dict())
        mongod.insertMarcap(retdto.dict())
        self.taskEventEmitter.emit(EVENT_TASK_REPO_TASK_COMPLETE)

