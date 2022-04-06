from pymitter import EventEmitter
from app.repo.FactorRepository import FactorRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.CrawlerRepository import CrawlerRepository
from app.module.socket.manager import ConnectionManager
from app.model.dao import FactorDao
from app.module.logger import Logger
from app.model.dto import ProcessTask, DartApiCrawling
from app.model.scrap.model import RunScrap, FactorDartRunScrap
from app.scrap.base.Scraper import Scraper
from app.scrap.FactorDartScraper import FactorDartScraper
from app.util.DartUtils import getMonthFromReprtCode
from app.util.AsyncUtil import batchFunction
from app.util.decorator import eventsDecorator
from typing import TYPE_CHECKING, Dict, List
import asyncio
import traceback
from app.base.BaseComponent import BaseComponent
from app.service.scrap.base.ScrapService import ScrapService
import uuid
if TYPE_CHECKING:
    from app.service.api.TaskApiService import TaskApiService


class FactorDartScrapService(ScrapService):
    
    def onComponentResisted(self) -> None:
        from app.service.api.TaskApiService import TaskApiService
        self.manager = self.get(ConnectionManager)
        self.factorRepository = self.get(FactorRepository)
        self.tasksRepository = self.get(TasksRepository)
        self.crawlerRepository = self.get(CrawlerRepository)
        self.taskApiService = self.get(TaskApiService)
        self.logger = Logger("FactorDartScrapService")
        return super().onComponentResisted()
    

    def createScraper(self) -> Scraper:
        return FactorDartScraper()
    

    async def convertRunDto(self, runDto: Dict) -> RunScrap:
        data = DartApiCrawling(**{
            "apiKey": runDto["apiKey"],
            "isCodeNew": runDto["isCodeNew"],
            "startYear": runDto["startYear"],
            "endYear": runDto["endYear"],
            "taskId": runDto["taskId"],
            "taskUniqueId": runDto["taskId"] + runDto["startYear"] + runDto["endYear"] + str(uuid.uuid4())
        })
        return data


    def createProcessTask(self, runCrawling: FactorDartRunScrap) -> ProcessTask:
        count = runCrawling.endYear - runCrawling.startYear + 1
        return ProcessTask(**{
            "market": "",
            "startDateStr": runCrawling.startYear,
            "endDateStr": runCrawling.endYear,
            "taskUniqueId": runCrawling.taskUniqueId,
            "taskId": runCrawling.taskId,
            "count": count,
            "tasks": list(range(runCrawling.startYear, runCrawling.endYear+1)),
            "restCount": count,
            "tasksRet": [0]*count,
            "state": "find worker"
        })
    

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
    
    @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_DOWNLOADING_CODES)
    async def onDownloadingCodes(self, dto: DartApiCrawling) -> None:
        self.logger.info("onDownloadingCodes", dto.taskUniqueId)
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download Codes"
        self.tasksRepository.updateTask(task)
    
    @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_CRAWLING_FACTOR_DATA)
    async def onCrawlingFactorData(self, dto: DartApiCrawling) -> None:
        self.logger.info("onCrawlingFactorData", dto.taskUniqueId)
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "crawling factor data"
        self.tasksRepository.updateTask(task)
    
    @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_COMPLETE_YEAR)
    async def onCompleteYear(self, dto: DartApiCrawling, year: int) -> None:
        self.logger.info("onCompleteYear", dto.taskUniqueId)
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        self.tasksRepository.completeTask(task, str(year))
    
    @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_RESULT_OF_FACTOR)
    async def onResultOfFactor(self, dto: DartApiCrawling, year: int, obj: List) -> None:
        self.logger.info("onResultOfFactor", dto.taskUniqueId)
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
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
    
    # @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_CANCEL)
    # def onCancel(self, dto: DartApiCrawling) -> None:
    #     self.logger.info("onCancelled")
        # self.logger.info("tasks", self.tasksRepository.tasksdto.json())
        # task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        # self.logger.info("task", task.json())
        # self.tasksRepository.fail(task, task.restCount)
        # task.state = "cancelled"
        # self.tasksRepository.updateTask(task)
        # self.logger.info("onCancelled", task.taskUniqueId)

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