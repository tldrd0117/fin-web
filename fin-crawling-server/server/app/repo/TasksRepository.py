from typing import Dict, List, Optional
from typing_extensions import Final

from pymitter import EventEmitter
from app.datasource.TaskMongoDataSource import TaskMongoDataSource
from app.model.dto import StockCrawlingCompletedTasks, StockMarketCapitalResult, StockCrawlingDownloadTask, StockUpdateState, \
    ProcessTasks, ProcessTask, StockTaskState, YearData
from app.model.dao import ListLimitDao, ListLimitDataDao
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
    def __init__(self, mongod: TaskMongoDataSource) -> None:
        super().__init__()
        self.mongod = mongod
        self.logger = Logger("TasksRepository")
        self.taskEventEmitter = EventEmitter()
        self.tasksdto = ProcessTasks()
        self.taskRunner: Optional[TaskRunner] = None
        self.createTaskRunner()
    
    # 태스크 러너를 만든다.
    def createTaskRunner(self) -> None:
        if self.taskRunner is None:
            self.taskRunner = TaskRunner()
            self.taskRunner.notifyCallback = self.onUpdatePoolInfo
            self.logger.info("createTaskRunner", "created taskrunner")

    # 태스크 풀 정보가 업데이트 될 떄 이벤트를 날린다.
    def onUpdatePoolInfo(self, poolInfo: TaskPoolInfo) -> None:
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_POOL_INFO, poolInfo)
        logger.info(f"updatePoolInfo:{poolInfo.json()}, {str(self)}")
        self.logger.info("updatePoolInfo", f"{poolInfo.json()}")
    
    # 테스크 풀 정보를 가져온다.
    def getPoolInfo(self) -> None:
        if self.taskRunner:
            poolInfo = self.taskRunner.getPoolInfo()
            self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_POOL_INFO, poolInfo)
    
    # 태스크 풀에 태스크를 등록한다.
    def runTask(self, task: Task) -> None:
        # print("runTask")
        if self.taskRunner:
            self.taskRunner.put(task)

    # 추가된 태스크 정보를 저장한다.
    def addTask(self, task: ProcessTask) -> None:
        if "marcap" not in self.tasksdto.tasks:
            self.tasksdto.tasks[task.taskId] = dict()
            self.tasksdto.tasks[task.taskId]["list"] = dict()
            self.tasksdto.tasks[task.taskId]["ids"] = []
            self.tasksdto.taskIds.append("marcap")
        self.tasksdto.tasks[task.taskId]["list"][task.taskUniqueId] = task
        self.tasksdto.tasks[task.taskId]["ids"].append(task.taskUniqueId)
        self.logger.info("addTask", f"{task.taskUniqueId}")

    # 갱신 태스크 정보를 저장한다.
    def updateTask(self, task: ProcessTask) -> None:
        self.tasksdto.tasks[task.taskId]["list"][task.taskUniqueId] = task
        self.logger.info("updateTask", f"{task.taskUniqueId}")
        self.mongod.upsertTask(task.dict())
        self.taskEventEmitter.emit(EVENT_TASK_REPO_UPDATE_TASKS, self.tasksdto)
    
    # 저장된 테스크 정보를 반환한다.
    def getTask(self, taskId: str, taskUniqueId: str) -> ProcessTask:
        if self.isExistTask(taskId, taskUniqueId):
            return self.tasksdto.tasks[taskId]["list"][taskUniqueId]
        return None
    
    # 저장된 태스크가 있는지 확인한다.
    def isExistTask(self, taskId: str, taskUniqueId: str) -> bool:
        return taskId in self.tasksdto.tasks and taskUniqueId in self.tasksdto.tasks[taskId]["list"]

    # 저장된 태스크 정보를 삭제한다.
    def deleteTask(self, task: ProcessTask) -> None:
        if task.taskId in self.tasksdto.tasks:
            if task.taskUniqueId in self.tasksdto.tasks[task.taskId]["list"]:
                del self.tasksdto.tasks[task.taskId]["list"][task.taskUniqueId]
                self.tasksdto.tasks[task.taskId]["ids"].remove(task.taskUniqueId)
                self.logger.info("deleteTask", f"{task.taskUniqueId}")
    
    def completeFactorConvertFileToDbTask(self, task: ProcessTask) -> None:
        self.success(task, 1)
        self.updateTask(task)
        self.taskEventEmitter.emit(EVENT_TASK_REPO_TASK_COMPLETE, "factorFile")

    # 완료된 태스크 정보를 처린한다.
    def completeStockCrawlingTask(self, isSuccess: bool, retdto: StockMarketCapitalResult, dto: StockCrawlingDownloadTask) -> None:
        task = self.getTask(dto.taskId, dto.taskUniqueId)
        if isSuccess:
            self.success(task, 1)
        else:
            self.fail(task, 1)
        if task.restCount <= 0:
            self.deleteTask(task)
        task.errMsg = retdto.errorMsg
        task.state = "complete"
        self.updateTask(task)
        self.logger.info("completeTask", "complete")
        self.taskEventEmitter.emit(EVENT_TASK_REPO_TASK_COMPLETE, "marcap", StockUpdateState(**{
            "taskId": dto.taskId,
            "market": dto.market,
            "date": dto.dateStr,
            "ret": 1 if isSuccess else 2
        }))
    
    # 성공한 태스크 정보를 처리한다.
    def success(self, task: ProcessTask, count: int) -> None:
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

    # 실패한 태스크 정보를 처리한다.
    def fail(self, task: ProcessTask, count: int) -> None:
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
    
    # 완료된 태스크 정보를 반환한다.
    def getCompletedTask(self, dto: ListLimitDao) -> ListLimitDataDao:
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

    # 모든 태스크 상태를 반환한다.
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
