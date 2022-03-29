from typing import List
from app.repo.StockRepository import StockRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.CrawlerRepository import CrawlerRepository
from app.scrap.MarcapScraper import MarcapScraper
from app.util.decorator import EventEmitter, eventsDecorator
from app.model.dto import StockMarketCapital, StockRunCrawling, \
    StockMarketCapitalResult, StockCrawlingDownloadTask, ProcessTask

from app.module.task import Pool, Task, TaskPool
from app.module.logger import Logger

import asyncio
from datetime import datetime, timedelta
from collections import deque
import traceback
from app.base.BaseComponent import BaseComponent
from app.service.scrap.base.ScrapService import ScrapService
from app.scrap.base.Scraper import Scraper
from app.scrap.SeibroDividendScraper import SeibroDividendScraper
from app.model.scrap.model import SeibroDividendRunScrap


class SeibroDividendScrapService(ScrapService):
    
    def onComponentResisted(self) -> None:
        self.stockRepository: StockRepository = self.get(StockRepository)
        self.tasksRepository: TasksRepository = self.get(TasksRepository)
        self.crawlerRepository: CrawlerRepository = self.get(CrawlerRepository)
        self.logger = Logger("SeibroDividendScrapService")
        return super().onComponentResisted()

    
    def createScraper(self) -> Scraper:
        return SeibroDividendScraper()
    

    async def convertRunDto(self, runCrawling: SeibroDividendRunScrap) -> SeibroDividendRunScrap:
        runCrawling.codes = await self.stockRepository.getMarcapCodes(runCrawling.startDate, runCrawling.endDate)
        return runCrawling
    

    def createProcessTask(self, runCrawling: SeibroDividendRunScrap) -> ProcessTask:
        startDate = datetime.strptime(runCrawling.startDate, "%Y%m%d")
        endDate = datetime.strptime(runCrawling.endDate, "%Y%m%d")
        taskDates = [(startDate + timedelta(days=x)).strftime("%Y%m%d") for x in range((endDate - startDate).days + 1)]
        return ProcessTask(**{
            "startDateStr": runCrawling.startDate,
            "endDateStr": runCrawling.endDate,
            "taskUniqueId": runCrawling.taskUniqueId,
            "taskId": runCrawling.taskId,
            "count": len(taskDates),
            "tasks": deque(taskDates),
            "restCount": len(taskDates),
            "tasksRet": deque(([0]*len(taskDates))),
        }) 

    
    # 주식 종목 데이터 크롤링 결과값을 db에 저장한다.
    @eventsDecorator.on(SeibroDividendScraper.EVENT_SEIBRO_DIVIDEND_ON_RESULT_OF_DATA)
    def onResultOfData(self, dto: StockCrawlingDownloadTask, retDto: StockMarketCapitalResult) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "insert to database"
        self.tasksRepository.updateTask(task)
        
        async def completeMarcapTask() -> None:
            await self.stockRepository.insertMarcap(retDto)
            self.tasksRepository.completeStockCrawlingTask(True, retDto, dto)
        asyncio.create_task(completeMarcapTask())

    # 크롤링 중 웹드라이버와 연결되었을 때 이벤트
    @eventsDecorator.on(SeibroDividendScraper.EVENT_SEIBRO_DIVIDEND_ON_CONNECTING_WEBDRIVER)
    def onConnectingWebdriver(self, dto: SeibroDividendRunScrap) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "connecting webdriver"
        self.tasksRepository.updateTask(task)
        self.logger.info("onConnectingWebDriver", task.taskUniqueId)

    # 크롤링이 시작되었을 떄 이벤트
    @eventsDecorator.on(SeibroDividendScraper.EVENT_SEIBRO_DIVIDEND_ON_START_CRAWLING)
    def onStartCrawling(self, dto: SeibroDividendRunScrap) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "start crawling"
        self.tasksRepository.updateTask(task)
        self.logger.info("onStartCrawling", task.taskUniqueId)
    
    # 크롤링 데이터 다운로드가 시작되었을 때 이벤트
    @eventsDecorator.on(SeibroDividendScraper.EVENT_SEIBRO_DIVIDEND_ON_END_CRAWLING)
    def onEndCrawling(self, dto: SeibroDividendRunScrap) -> None:
        # self.logger.info("onDownloadStart: "+dto.json())
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "end crawling"
        self.tasksRepository.updateTask(task)
        self.logger.info("onEndCrawling", task.taskUniqueId)

    # 크롤링이 취소되었을 때 이벤트
    @eventsDecorator.on(SeibroDividendScraper.EVENT_SEIBRO_DIVIDEND_ON_CANCEL)
    def onCancel(self, dto: SeibroDividendRunScrap) -> None:
        self.logger.info("onCancel")
        # self.tasksRepository.updateAllTask()
        # task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        # self.tasksRepository.fail(task, task.restCount)
        # task.state = "cancelled"
        # self.tasksRepository.updateTask(task)
        # self.logger.info("onCancelled", task.taskUniqueId)
    
    # 크롤링이 에러가났을 때 이벤트\
    @eventsDecorator.on(SeibroDividendScraper.EVENT_SEIBRO_DIVIDEND_ON_ERROR)
    def onError(self, dto: SeibroDividendRunScrap, errorMsg: str) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        self.tasksRepository.fail(task, task.restCount)
        task.state = "error"
        task.errMsg = errorMsg
        self.tasksRepository.updateTask(task)
        self.logger.error("onError", task.taskUniqueId)

    
