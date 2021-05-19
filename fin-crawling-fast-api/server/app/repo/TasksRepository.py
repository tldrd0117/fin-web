from typing import Any, Callable
from app.crawler.MarcapCrawler import marcapCrawler, ee, \
    EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, \
    EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_START_CRAWLING
from app.model.dto import StockCrawlingDownloadTaskDTO, StockCrawlingRunCrawlingDTO, StockCrawlingTasksDTO, StockMarketCapitalResultDTO, StockCrawlingTaskDTO
import asyncio

SUCCESS = 1
FAIL = 2
WAIT = 0


class Task(object):
    def __init__(self, func: Callable, param: Any) -> None:
        super().__init__()
        self.func = func
        self.param = param

    def run(self) -> None:
        asyncio.create_task(self.func(self.param))


class TaskRunner(object):
    def __init__(self) -> None:
        super().__init__()
        self.queue: asyncio.Queue = asyncio.Queue()
    
    def run(self) -> None:
        asyncio.create_task(self._run())

    def put(self, task: Task) -> None:
        asyncio.create_task(self._put(task))

    async def _run(self) -> None:
        while True:
            task: Task = await self.queue.get()
            task.run()

    async def _put(self, task: Task) -> None:
        await self.queue.put(task)


class TasksRepository(object):
    def __init__(self) -> None:
        super().__init__()
        self.taskRunner = TaskRunner()
        self.taskRunner.run()
        self.createListners()
        self.tasksdto = StockCrawlingTasksDTO()

    def runTask(self, task: Task) -> None:
        self.taskRunner.put(task)

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

    def createListners(self) -> None:
        @ee.on(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER)
        def onConnectingWebDriver(dto: StockCrawlingRunCrawlingDTO) -> None:
            task = StockCrawlingTaskDTO(**{
                "market": dto.market,
                "startDateStr": dto.startDateStr,
                "endDateStr": dto.endDateStr,
                "taskUniqueId": dto.taskUniqueId,
                "taskId": dto.taskId
            })
            task.state = "connecting webdriver"
            self.addTask(task)
            # self.ee.emit("crawling/updateTasks", self.tasks)

        @ee.on(EVENT_MARCAP_CRAWLING_ON_START_CRAWLING)
        def onStartCrawling(dto: StockCrawlingRunCrawlingDTO) -> None:
            task = self.getTask(dto.taskId, dto.taskUniqueId)
            task.state = "start crawling"
            self.tasksdto.updateTask(task)
            # self.ee.emit("crawling/updateTasks", self.tasks)
            # self.ee.emit("crawlingService/upsertTask", task)
       

        @ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START)
        def onDownloadStart(dto: StockCrawlingDownloadTaskDTO) -> None:
            task = self.getTask(dto.taskId, dto.taskUniqueId)
            task.state = "download start"
            self.tasksdto.updateTask(task)
            # self.ee.emit("crawling/updateTasks", self.tasks)
            # self.ee.emit("crawlingService/upsertTask", task)

        @ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE)
        def onDownloadComplete(dto: StockCrawlingDownloadTaskDTO) -> None:
            task = self.getTask(dto.taskId, dto.taskUniqueId)
            task.state = "download complete"
            self.tasksdto.updateTask(task)
            # self.ee.emit("crawling/updateTasks", self.tasks)
            # self.ee.emit("crawlingService/upsertTask", task)

        @ee.on(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE)
        def onParsingComplete(isSuccess: bool, retdto: StockMarketCapitalResultDTO, dto: StockCrawlingDownloadTaskDTO) -> None:
            task = self.getTask(dto.taskId, dto.taskUniqueId)
            if isSuccess:
                self.success(task, 1)
            else:
                self.fail(task, 1)
            self.tasksdto.updateTask(task)
            # self.ee.emit("crawling/updateTasks", self.tasks)
            # self.ee.emit("crawlingService/upsertTask", task)
            # self.ee.emit("crawlingService/upsertData", ret)
    

