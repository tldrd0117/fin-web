from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Final, List, Optional

from pymitter import EventEmitter
from app.crawler.MarcapCrawler import EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, \
    EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, \
    EVENT_MARCAP_CRAWLING_ON_ERROR, \
    EVENT_MARCAP_CRAWLING_ON_CANCEL
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.model.dto import StockUpdateState, StockCrawlingCompletedTasks, StockCrawlingDownloadTask, StockCrawlingRunCrawling, StockCrawlingTasks, StockMarketCapitalResult, StockCrawlingTask, StockTaskState, ListLimitData, ListLimitResponse, YearData
from app.model.task import TaskPoolInfo
from app.module.task import Task, TaskRunner
from app.module.logger import Logger


from uvicorn.config import logger

SUCCESS: Final = 1
FAIL: Final = 2
WAIT: Final = 0

EVENT_TASK_REPO_UPDATE_TASKS = "taskRepo/updateTasks"
EVENT_TASK_REPO_TASK_COMPLETE = "taskRepo/completeTask"
EVENT_TASK_REPO_UPDATE_POOL_INFO = "taskRepo/updatePoolInfo"


class TasksRepository(object):
    def __init__(self, mongod: StockMongoDataSource) -> None:
        super().__init__()
        self.mongod = mongod
        self.logger = Logger("TasksRepository")
        self.taskEventEmitter = EventEmitter()
        self.tasksdto = StockCrawlingTasks()
        self.taskRunner: Optional[TaskRunner] = None
        self.createTaskRunner()
    
    def createTaskRunner(self) -> None:
        if self.taskRunner is None:
            self.taskRunner = TaskRunner()
            self.taskRunner.notifyCallback = self.updatePoolInfo
            self.logger.info("createTaskRunner", "created taskrunner")

    def updatePoolInfo(self, poolInfo: TaskPoolInfo) -> None:
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_POOL_INFO, poolInfo)
        logger.info(f"updatePoolInfo:{poolInfo.json()}, {str(self)}")
        self.logger.info("updatePoolInfo", f"{poolInfo.json()}")
    
    def getPoolInfo(self) -> None:
        if self.taskRunner:
            poolInfo = self.taskRunner.getPoolInfo()
            self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_POOL_INFO, poolInfo)
    
    def runTask(self, task: Task) -> None:
        # print("runTask")
        if self.taskRunner:
            self.taskRunner.put(task)
    
    def runMarcapTask(self, workerTask: Task, dto: StockCrawlingRunCrawling) -> None:
        if self.taskRunner:
            if self.isExistTask(dto.taskId, dto.taskUniqueId):
                return
            startDate = datetime.strptime(dto.startDateStr, "%Y%m%d")
            endDate = datetime.strptime(dto.endDateStr, "%Y%m%d")
            taskDates = [(startDate + timedelta(days=x)).strftime("%Y%m%d") for x in range((endDate - startDate).days + 1)]
            task = StockCrawlingTask(**{
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
            self.logger.info("runMarcapTask", f"runTask {task.json()}")

    def addTask(self, task: StockCrawlingTask) -> None:
        if "marcap" not in self.tasksdto.tasks:
            self.tasksdto.tasks[task.taskId] = dict()
            self.tasksdto.tasks[task.taskId]["list"] = dict()
            self.tasksdto.tasks[task.taskId]["ids"] = []
            self.tasksdto.taskIds.append("marcap")
        self.tasksdto.tasks[task.taskId]["list"][task.taskUniqueId] = task
        self.tasksdto.tasks[task.taskId]["ids"].append(task.taskUniqueId)
        self.logger.info("addTask", f"{task.taskUniqueId}")

    def updateTask(self, task: StockCrawlingTask) -> None:
        self.tasksdto.tasks[task.taskId]["list"][task.taskUniqueId] = task
        self.logger.info("updateTask", f"{task.taskUniqueId}")
    
    def getTask(self, taskId: str, taskUniqueId: str) -> StockCrawlingTask:
        if self.isExistTask(taskId, taskUniqueId):
            return self.tasksdto.tasks[taskId]["list"][taskUniqueId]
        return None
    
    def isExistTask(self, taskId: str, taskUniqueId: str) -> bool:
        return taskId in self.tasksdto.tasks and taskUniqueId in self.tasksdto.tasks[taskId]["list"]

    def deleteTask(self, task: StockCrawlingTask) -> None:
        if task.taskId in self.tasksdto.tasks:
            if task.taskUniqueId in self.tasksdto.tasks[task.taskId]["list"]:
                del self.tasksdto.tasks[task.taskId]["list"][task.taskUniqueId]
                self.tasksdto.tasks[task.taskId]["ids"].remove(task.taskUniqueId)
                self.logger.info("deleteTask", f"{task.taskUniqueId}")
    
    def success(self, task: StockCrawlingTask, count: int) -> None:
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
        self.logger.info("success", f"{task.taskUniqueId}")

    def fail(self, task: StockCrawlingTask, count: int) -> None:
        task.failCount = task.failCount + count
        task.restCount = task.restCount - count
        i = 0
        for _ in range(count):
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
        self.logger.info("fail", f"{task.taskUniqueId}")
    
    def getCompletedTask(self, dto: ListLimitData) -> ListLimitResponse:
        taskData = self.mongod.getCompletedTask(dto)
        tasks: Dict = dict()
        taskIds = []
        for task in taskData.data:
            if task["taskId"] not in tasks:
                tasks[task["taskId"]] = dict()
                tasks[task["taskId"]]["list"] = dict()
                tasks[task["taskId"]]["ids"] = []
                taskIds.append(task["taskId"])
            tasks[task["taskId"]]["list"][task["taskUniqueId"]] = task
            tasks[task["taskId"]]["ids"].append(task["taskUniqueId"])
            
        stockCrawlingCompletedTasksDTO = StockCrawlingCompletedTasks(**{
            "history": tasks,
            "historyIds": taskIds
        })
        taskData.data = stockCrawlingCompletedTasksDTO
        self.logger.info("getCompletedTask", f"count: {len(taskIds)}")
        return taskData

    def getAllTaskState(self, taskId: str) -> StockTaskState:
        markets = ["kospi", "kosdaq"]
        resultDict: YearData = YearData(**{
            "yearData": dict()
        })
        resultDict.yearData[taskId] = dict()
        for market in markets:
            data = self.mongod.getAllTaskState(taskId, market)
            compDict: Dict = {}
            count: Dict = {}
            for one in data:
                for idx, taskDate in enumerate(one["tasks"]):
                    if taskDate in compDict.keys():
                        if compDict[taskDate]["ret"] == 1 or one["tasksRet"][idx] == 1:
                            compDict[taskDate] = {"date": taskDate, "ret": 1}
                    else:
                        year = taskDate[0:4]
                        if year in count.keys():
                            count[year] = count[year] + 1
                        else:
                            count[year] = 1
                        compDict[taskDate] = {"date": taskDate, "ret": one["tasksRet"][idx]}
            collect: List = list(compDict.values())
            collect = sorted(collect, key=lambda x: x["date"])
            resultDict.yearData[taskId][market] = StockTaskState(**{
                "taskStates": compDict,
                "taskKeys": compDict.keys(),
                "stocks": collect,
                "years": count,
                "market": market,
                "taskId": taskId
            })
        return resultDict

    def createListners(self, ee: EventEmitter) -> None:
        ee.on(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, self.onConnectingWebDriver)
        ee.on(EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, self.onStartCrawling)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, self.onDownloadStart)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, self.onDownloadComplete)
        ee.on(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, self.onParsingComplete)
        ee.on(EVENT_MARCAP_CRAWLING_ON_ERROR, self.onError)
        ee.on(EVENT_MARCAP_CRAWLING_ON_CANCEL, self.onCancelled)
    
    def onConnectingWebDriver(self, dto: StockCrawlingRunCrawling) -> None:
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "connecting webdriver"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        self.mongod.upsertTask(task.dict())
        self.logger.info("onConnectingWebDriver", task.taskUniqueId)

    def onStartCrawling(self, dto: StockCrawlingRunCrawling) -> None:
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "start crawling"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        self.mongod.upsertTask(task.dict())
        self.logger.info("onStartCrawling", task.taskUniqueId)
    
    def onDownloadStart(self, dto: StockCrawlingDownloadTask) -> None:
        logger.info("onDownloadStart: "+dto.json())
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download start"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        self.mongod.upsertTask(task.dict())
        self.logger.info("onDownloadStart", task.taskUniqueId)

    def onDownloadComplete(self, dto: StockCrawlingDownloadTask) -> None:
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download complete"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        self.mongod.upsertTask(task.dict())
        self.logger.info("onDownloadComplete", task.taskUniqueId)

    def onParsingComplete(self, isSuccess: bool, retdto: StockMarketCapitalResult, dto: StockCrawlingDownloadTask) -> None:
        logger.info("onParsingComplete")
        logger.info(f"taskId:{dto.taskId} taskUniqueId{dto.taskUniqueId}")
        tar = self.tasksdto.tasks[dto.taskId]["list"]
        logger.info(f"taskDTO: {tar}")
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        if isSuccess:
            self.success(task, 1)
        else:
            self.fail(task, 1)
        if task.restCount <= 0:
            self.deleteTask(task)
        task.errMsg = retdto.errorMsg
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        self.mongod.upsertTask(task.dict())
        self.taskEventEmitter.emit(EVENT_TASK_REPO_TASK_COMPLETE, "marcap", StockUpdateState(**{
            "taskId": dto.taskId,
            "market": dto.market,
            "date": dto.dateStr,
            "ret": 1 if isSuccess else 2
        }))
        self.logger.info("onParsingComplete", task.taskUniqueId)
    
    def onCancelled(self, dto: StockCrawlingRunCrawling) -> None:
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        self.fail(task, task.restCount)
        task.state = "cancelled"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        self.mongod.upsertTask(task.dict())
        self.logger.info("onCancelled", task.taskUniqueId)
    
    def onError(self, dto: StockCrawlingRunCrawling) -> None:
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        self.fail(task, task.restCount)
        task.state = "error"
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
        self.mongod.upsertTask(task.dict())
        self.logger.error("onError", task.taskUniqueId)

