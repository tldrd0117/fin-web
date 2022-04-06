from typing import Any, Dict, List
from app.repo.StockRepository import StockRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.CrawlerRepository import CrawlerRepository
from app.scrap.MarcapScraper import MarcapScraper
from app.scrap.base.Scraper import Scraper
from app.service.scrap.base.ScrapService import ScrapService
from app.util.decorator import eventsDecorator
from app.model.dto import StockMarketCapital, \
    StockMarketCapitalResult, StockCrawlingDownloadTask, ProcessTask

from app.model.scrap.model import MarcapRunScrap, RunScrap

from app.module.task import Pool, Task, TaskPool
from app.module.logger import Logger
from app.util.DateUtils import getNowDateStr

import asyncio
from datetime import datetime, timedelta
from collections import deque
import traceback
import uuid


class MarcapScrapService(ScrapService):

    
    def onComponentResisted(self) -> None:
        self.stockRepository: StockRepository = self.get(StockRepository)
        self.tasksRepository: TasksRepository = self.get(TasksRepository)
        self.crawlerRepository: CrawlerRepository = self.get(CrawlerRepository)
        self.logger = Logger("MarcapScrapService")
        return super().onComponentResisted()
    

    def createScraper(self) -> Scraper:
        return MarcapScraper()
    

    async def convertRunDto(self, runDto: dict) -> List[RunScrap]:
        data = []
        if "isNow" in runDto and runDto["isNow"]:
            runDto["startDate"] = getNowDateStr()
            runDto["endDate"] = getNowDateStr()
        
        for market in runDto["market"]:
            taskUniqueId = runDto["taskId"]+market+runDto["startDate"]+runDto["endDate"]+str(uuid.uuid4())
            dtoOne = MarcapRunScrap(**{
                "driverAddr": "http://fin-crawling-webdriver:4444",
                "market": market,
                "startDateStr": runDto["startDate"],
                "endDateStr": runDto["endDate"],
                "taskId": runDto["taskId"],
                "taskUniqueId": taskUniqueId
            })
            data.append(dtoOne)
        return data
            
    

    def createProcessTask(self, runCrawling: MarcapRunScrap) -> ProcessTask:
        startDate = datetime.strptime(runCrawling.startDateStr, "%Y%m%d")
        endDate = datetime.strptime(runCrawling.endDateStr, "%Y%m%d")
        taskDates = [(startDate + timedelta(days=x)).strftime("%Y%m%d") for x in range((endDate - startDate).days + 1)]
        return ProcessTask(**{
            "market": runCrawling.market,
            "startDateStr": runCrawling.startDateStr,
            "endDateStr": runCrawling.endDateStr,
            "taskUniqueId": runCrawling.taskUniqueId,
            "taskId": runCrawling.taskId,
            "count": len(taskDates),
            "tasks": deque(taskDates),
            "restCount": len(taskDates),
            "tasksRet": deque(([0]*len(taskDates))),
        })
                
    
    # 주식 종목 데이터 크롤링 결과값을 db에 저장한다.
    @eventsDecorator.on(MarcapScraper.EVENT_MARCAP_CRAWLING_ON_RESULT_OF_STOCK_DATA)
    async def onResultOfStockData(self, dto: StockCrawlingDownloadTask, retDto: StockMarketCapitalResult) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "insert to database"
        self.tasksRepository.updateTask(task)
        async def insertTask() -> None:
            await self.stockRepository.insertMarcap(retDto)
            self.tasksRepository.completeTask(task, dto.dateStr)
        asyncio.create_task(insertTask())

    # 크롤링 중 웹드라이버와 연결되었을 때 이벤트
    @eventsDecorator.on(MarcapScraper.EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER)
    async def onConnectingWebDriver(self, dto: MarcapRunScrap) -> None:
        self.logger.info("eventsDecorator on")
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "connecting webdriver"
        self.tasksRepository.updateTask(task)
        self.logger.info("onConnectingWebDriver", task.taskUniqueId)

    # 크롤링이 시작되었을 떄 이벤트
    @eventsDecorator.on(MarcapScraper.EVENT_MARCAP_CRAWLING_ON_START_CRAWLING)
    async def onStartCrawling(self, dto: MarcapRunScrap) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "start crawling"
        self.tasksRepository.updateTask(task)
        self.logger.info("onStartCrawling", task.taskUniqueId)
    
    # 크롤링 데이터 다운로드가 시작되었을 때 이벤트
    @eventsDecorator.on(MarcapScraper.EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START)
    async def onDownloadStart(self, dto: StockCrawlingDownloadTask) -> None:
        # self.logger.info("onDownloadStart: "+dto.json())
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download start"
        self.tasksRepository.updateTask(task)
        self.logger.info("onDownloadStart", task.taskUniqueId)

    # 크롤링 데이터 다운로드가 완료되었을 때 이벤트
    @eventsDecorator.on(MarcapScraper.EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE)
    async def onDownloadComplete(self, dto: StockCrawlingDownloadTask) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download complete"
        self.tasksRepository.updateTask(task)
        self.logger.info("onDownloadComplete", task.taskUniqueId)

    # 크롤링 데이터 변환이 완료되었을 때 이벤트
    @eventsDecorator.on(MarcapScraper.EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE)
    async def onParsingComplete(self, isSuccess: bool, retdto: StockMarketCapitalResult, dto: StockCrawlingDownloadTask) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "parsing complete"
        self.tasksRepository.updateTask(task)
    
    # # 크롤링이 취소되었을 때 이벤트
    # @eventsDecorator.on(MarcapScraper.EVENT_MARCAP_CRAWLING_ON_CANCEL)
    # def onCancel(self, dto: MarcapRunScrap) -> None:
    #     self.logger.info("onCancelled")
    #     # self.tasksRepository.updateAllTask()
    #     # task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
    #     # self.tasksRepository.fail(task, task.restCount)
    #     # task.state = "cancelled"
    #     # self.tasksRepository.updateTask(task)
    #     # self.logger.info("onCancelled", task.taskUniqueId)
    
    # # 크롤링이 에러가났을 때 이벤트
    # @eventsDecorator.on(MarcapScraper.EVENT_MARCAP_CRAWLING_ON_ERROR)
    # def onError(self, dto: MarcapRunScrap, errorMsg: str) -> None:
    #     task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
    #     self.tasksRepository.fail(task, task.restCount)
    #     task.state = "error"
    #     task.errMsg = errorMsg
    #     self.tasksRepository.updateTask(task)
    #     self.logger.error("onError", task.taskUniqueId)

    
