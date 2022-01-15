from pymitter import EventEmitter
from app.repo.FactorRepository import FactorRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.CrawlerRepository import CrawlerRepository
from app.module.socket.manager import ConnectionManager
from app.model.dao import FactorDao
from app.module.logger import Logger
from app.module.task import Pool, Task, TaskPool
from app.model.dto import ProcessTask, RunFactorFileConvert, DartApiCrawling
from app.crawler.DartApiCrawler import DartApiCrawler, \
    EVENT_DART_API_CRAWLING_ON_DOWNLOADING_CODES, \
    EVENT_DART_API_CRAWLING_ON_CRAWLING_FACTOR_DATA, \
    EVENT_DART_API_CRAWLING_ON_COMPLETE_YEAR, \
    EVENT_DART_API_CRAWLING_ON_RESULT_OF_FACTOR
from app.util.DartUtils import getMonthFromReprtCode
from typing import TYPE_CHECKING, Dict, List
import asyncio
import traceback
if TYPE_CHECKING:
    from app.service.TaskService import TaskService


RES_SOCKET_FACTOR_UPDATE_STATE_RES = "factor/updateConvertStateRes"

RES_SOCKET_FACTOR_FETCH_COMPLETED_TASK = "factor/fetchCompletedTaskRes"
RES_SOCKET_FACTOR_FETCH_TASKS = "factor/fetchTasksRes"


class FactorService:
    def __init__(self, manager: ConnectionManager, factorRepository: FactorRepository, tasksRepository: TasksRepository, crawlerRepository: CrawlerRepository, taskService: 'TaskService') -> None:
        self.manager = manager
        self.factorRepository = factorRepository
        self.tasksRepository = tasksRepository
        self.crawlerRepository = crawlerRepository
        self.taskService = taskService
        self.logger = Logger("FactorService")

    def crawlingFactorDartData(self, dto: DartApiCrawling) -> None:
        async def crawlingFactorDartDataTask(pool: Pool, taskPool: TaskPool) -> None:
            # task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
            try:
                crawler = DartApiCrawler()
                self.crawlerRepository.addCrawler(dto.taskUniqueId, crawler)
                self.createFactorDartListener(crawler.ee)
                await crawler.crawling(dto)
                self.crawlerRepository.removeCrawler(crawler)
            except Exception:
                self.logger.error("crawlingFactorDartDataTask", f"error: {traceback.format_exc()}")
                task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
                task.state = "error"
                task.errMsg = traceback.format_exc()
                self.tasksRepository.updateTask(task)
            finally:
                taskPool.removeTaskPool(pool)

        count = dto.endYear - dto.startYear + 1
        task = ProcessTask(**{
            "market": "",
            "startDateStr": dto.startYear,
            "endDateStr": dto.endYear,
            "taskUniqueId": dto.taskUniqueId,
            "taskId": dto.taskId,
            "count": 1,
            "tasks": list(range(dto.startYear, dto.endYear+1)),
            "restCount": count,
            "tasksRet": [0]*count,
            "state": "find worker"
        })
        self.tasksRepository.addTask(task)
        workerTask = Task(dto.taskUniqueId, crawlingFactorDartDataTask)
        self.tasksRepository.runTask(workerTask)
    
    def cancelCrawling(self, dto: DartApiCrawling) -> None:
        if dto.taskUniqueId in self.crawlerRepository.getCrawlers():
            self.tasksRepository.taskRunner.cancel(dto.taskUniqueId)
            self.crawlerRepository.getCrawler(dto.taskUniqueId).isCancelled = True
        else:
            task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
            if task is not None:
                self.tasksRepository.deleteTask(task)
    
    def cancelFactorFileToDb(self, dto: RunFactorFileConvert) -> None:
        if self.tasksRepository.taskRunner.isExist(dto.taskUniqueId):
            self.tasksRepository.taskRunner.cancel(dto.taskUniqueId)
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        if task is not None:
            self.tasksRepository.deleteTask(task)
        
    # file에 있는 factor를 db에 저장한다.
    def convertFactorFileToDb(self, dto: RunFactorFileConvert) -> None:
        self.logger.info("convertFactorFileToDb")

        async def convertFactorFileToDbTask(pool: Pool, taskPool: TaskPool) -> None:
            try:
                task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
                data = await self.factorRepository.getFactorsInFile()
                task.state = "start insert db"
                self.tasksRepository.updateTask(task)
                daoList = await self.makeFactorDaoList(data)
                self.logger.info("convertFactorFileToDbTask", f"insertCount: {str(len(daoList))}")
                await self.factorRepository.insertFactor(daoList)
                task.state = "complete"
                self.tasksRepository.completeFactorConvertFileToDbTask(task)
            except Exception:
                self.logger.error("convertFactorFileToDbTask", f"error: {traceback.format_exc()}")
                task.state = "error"
                task.errMsg = traceback.format_exc()
                self.tasksRepository.updateTask(task)
            finally:
                taskPool.removeTaskPool(pool)
        task = ProcessTask(**{
            "market": "",
            "startDateStr": "20070101",
            "endDateStr": "20191231",
            "taskUniqueId": dto.taskUniqueId,
            "taskId": dto.taskId,
            "count": 1,
            "tasks": ["convert"],
            "restCount": 1,
            "tasksRet": [0],
            "state": "start get file"
        })
        self.tasksRepository.addTask(task)
        workerTask = Task(dto.taskUniqueId, convertFactorFileToDbTask)
        self.tasksRepository.runTask(workerTask)
    
    async def makeFactorDaoList(self, data: List[Dict]) -> List[FactorDao]:
        daoList = []
        for one in data:
            dao = FactorDao(**{
                "code": one["종목코드"],       # 종목코드
                "name": one["종목명"],       # 종목이름
                "dataYear": one["년"],      # 결산년
                "dataMonth": one["결산월"],  # 결산월
                "dataName": one["데이터명"],   # 데이터명
                "dataValue": (one["데이터값"] * 1000) if one["단위"] == "천원" else one["데이터값"]  # 데이터값
            })
            daoList.append(dao)
        return daoList
    
    def createFactorDartListener(self, ee: EventEmitter) -> None:
        ee.on(EVENT_DART_API_CRAWLING_ON_DOWNLOADING_CODES, self.onDownloadingCodes)
        ee.on(EVENT_DART_API_CRAWLING_ON_CRAWLING_FACTOR_DATA, self.onCrawlingFactorData)
        ee.on(EVENT_DART_API_CRAWLING_ON_COMPLETE_YEAR, self.onCompleteYear)
        ee.on(EVENT_DART_API_CRAWLING_ON_RESULT_OF_FACTOR, self.onResultOfFactor)
    
    def onDownloadingCodes(self, dto: DartApiCrawling) -> None:
        self.logger.info("onDownloadingCodes", dto.taskUniqueId)
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download Codes"
        self.tasksRepository.updateTask(task)
    
    def onCrawlingFactorData(self, dto: DartApiCrawling) -> None:
        self.logger.info("onCrawlingFactorData", dto.taskUniqueId)
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "crawling factor data"
        self.tasksRepository.updateTask(task)
    
    def onCompleteYear(self, dto: DartApiCrawling, year: int) -> None:
        self.logger.info("onCompleteYear", dto.taskUniqueId)
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        self.tasksRepository.completeFactorDart(task, year)
    
    def onResultOfFactor(self, dto: DartApiCrawling, year: int, obj: List) -> None:
        self.logger.info("onResultOfFactor", dto.taskUniqueId)
        listOfFactorDao = list(map(lambda one: FactorDao(**{
            "code": one["crawling_code"],
            "name": one["crawling_name"],
            "dataYear": one["bsns_year"],
            "dataMonth": getMonthFromReprtCode(one["reprt_code"]),
            "dataName": one["account_nm"],
            "dataValue": one["thstrm_amount"],
            "dataId": one["account_id"]
        }), obj))
        asyncio.create_task(self.factorRepository.insertFactorDart(listOfFactorDao))

    # def createTaskRepositoryListener(self) -> None:
        # self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_TASK_COMPLETE, self.completeTask)
        # self.tasksRepository.taskEventEmitter.on(EVENT_TASK_REPO_UPDATE_TASKS, self.updateTasks)
    
    # def updateTasks(self) -> None:
        # self.manager.sendBroadCast(RES_SOCKET_FACTOR_FETCH_TASKS, self.tasksRepository.tasksdto.dict())
    
    # def completeTask(self) -> None:
    #     dto = ListLimitData(**{
    #         "offset": 0,
    #         "limit": 20
    #     })
    #     tasks: StockCrawlingCompletedTasks = self.tasksRepository.getCompletedTask(dto)
    #     self.manager.sendBroadCast(RES_SOCKET_FACTOR_FETCH_COMPLETED_TASK, tasks.dict())
    
    # def fetchCompletedTask(self, dto: ListLimitData, webSocket: WebSocket) -> None:
    #     listLimitDao = ListLimitDao(**{
    #         "offset": dto["offset"],
    #         "limit": dto["limit"],
    #         "taskId": "factorFile"
    #     })
    #     tasks: ListLimitDataDao = self.tasksRepository.getCompletedTask(listLimitDao)
    #     # logger.info("histories:"+tasks.json())
    #     self.manager.send(RES_SOCKET_FACTOR_FETCH_COMPLETED_TASK, tasks.dict(), webSocket)