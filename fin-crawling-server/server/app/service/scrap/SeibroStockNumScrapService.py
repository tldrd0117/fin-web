from typing import Dict, List
from app.repo.StockRepository import StockRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.FactorRepository import FactorRepository
from app.scrap.MarcapScraper import MarcapScraper
from app.util.decorator import eventsDecorator
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
from app.scrap.SeibroStockNumScraper import SeibroStockNumScraper
from app.model.scrap.model import SeibroStockNumRunScrap
import uuid


class SeibroStockNumScrapService(ScrapService):
    
    def onComponentResisted(self) -> None:
        self.stockRepository: StockRepository = self.get(StockRepository)
        self.tasksRepository: TasksRepository = self.get(TasksRepository)
        self.factorRepository: FactorRepository = self.get(FactorRepository)
        self.crawlerRepository: CrawlerRepository = self.get(CrawlerRepository)
        self.logger = Logger("SeibroStockNumScrapService")
        return super().onComponentResisted()

    
    def createScraper(self) -> Scraper:
        return SeibroStockNumScraper()
    

    async def convertRunDto(self, runDict: Dict ) -> SeibroStockNumRunScrap:
        self.logger.info("convertRunDto", str(runDict))
        codes = await self.stockRepository.getMarcapCodes(runDict["startDate"], runDict["endDate"])
        taskUniqueId = runDict["taskId"]+runDict["startDate"]+runDict["endDate"]+str(uuid.uuid4())
        runDto = SeibroStockNumRunScrap(**{
            "driverAddr": "http://fin-crawling-webdriver:4444",
            "startDate": runDict["startDate"],
            "codes": codes,
            "endDate": runDict["endDate"],
            "taskId": runDict["taskId"],
            "taskUniqueId": taskUniqueId
        })
        return runDto
    

    def createProcessTask(self, runDto: SeibroStockNumRunScrap) -> ProcessTask:
        return ProcessTask(**{
            "startDateStr": runDto.startDate,
            "endDateStr": runDto.endDate,
            "taskUniqueId": runDto.taskUniqueId,
            "taskId": runDto.taskId,
            "count": len(runDto.codes),
            "tasks": deque(runDto.codes),
            "restCount": len(runDto.codes),
            "tasksRet": deque(([0]*len(runDto.codes))),
        }) 

    
    # 주식 종목 데이터 크롤링 결과값을 db에 저장한다.
    @eventsDecorator.on(SeibroStockNumScraper.EVENT_SEIBRO_STOCK_NUM_ON_RESULT_OF_DATA)
    async def onResultOfData(self, dto: SeibroStockNumRunScrap, data: list) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "insert to database"
        self.tasksRepository.updateTask(task)
        
        async def insertTask() -> None:
            await self.factorRepository.insertFactorSeibroStockNum(data)
            self.tasksRepository.completeTask(task, "")
        await asyncio.create_task(insertTask())


    # 크롤링 중 웹드라이버와 연결되었을 때 이벤트
    @eventsDecorator.on(SeibroStockNumScraper.EVENT_SEIBRO_STOCK_NUM_ON_CONNECTING_WEBDRIVER)
    async def onConnectingWebdriver(self, dto: SeibroStockNumRunScrap) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "connecting webdriver"
        self.tasksRepository.updateTask(task)
        self.logger.info("onConnectingWebDriver", task.taskUniqueId)

    # 크롤링이 시작되었을 떄 이벤트
    @eventsDecorator.on(SeibroStockNumScraper.EVENT_SEIBRO_STOCK_NUM_ON_START_CRAWLING)
    async def onStartCrawling(self, dto: SeibroStockNumRunScrap) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "start crawling"
        self.tasksRepository.updateTask(task)
        self.logger.info("onStartCrawling", task.taskUniqueId)
    
    # 크롤링 데이터 다운로드가 시작되었을 때 이벤트
    @eventsDecorator.on(SeibroStockNumScraper.EVENT_SEIBRO_STOCK_NUM_ON_END_CRAWLING)
    async def onEndCrawling(self, dto: SeibroStockNumRunScrap) -> None:
        # self.logger.info("onDownloadStart: "+dto.json())
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "end crawling"
        self.tasksRepository.updateTask(task)
        self.logger.info("onEndCrawling", task.taskUniqueId)
