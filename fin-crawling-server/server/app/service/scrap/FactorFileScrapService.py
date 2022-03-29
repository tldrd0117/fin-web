from typing import Dict, List
from app.repo.StockRepository import StockRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.CrawlerRepository import CrawlerRepository
from app.repo.FactorRepository import FactorRepository
from app.scrap.MarcapScraper import MarcapScraper
from app.scrap.base.Scraper import Scraper
from app.scrap.FactorFileScraper import FactorFileScraper
from app.service.scrap.base.ScrapService import ScrapService
from app.util.decorator import eventsDecorator
from app.model.dto import StockMarketCapital, \
    StockMarketCapitalResult, StockCrawlingDownloadTask, ProcessTask
from app.model.dao import FactorDao

from app.model.scrap.model import MarcapRunScrap, RunScrap

from app.module.task import Pool, Task, TaskPool
from app.module.logger import Logger

import asyncio
from datetime import datetime, timedelta
from collections import deque
import traceback
from app.util.AsyncUtil import batchFunction
import uuid
from app.model.scrap.model import FactorFileRunScrap


class FactorFileScrapService(ScrapService):
    
    def onComponentResisted(self) -> None:
        self.stockRepository: StockRepository = self.get(StockRepository)
        self.tasksRepository: TasksRepository = self.get(TasksRepository)
        self.crawlerRepository: CrawlerRepository = self.get(CrawlerRepository)
        self.factorRepository: FactorRepository = self.get(FactorRepository)
        self.logger = Logger("FactorFileScrapService")
        return super().onComponentResisted()
    

    def createScraper(self) -> Scraper:
        return FactorFileScraper(self)
    

    async def convertRunDto(self, runDto: dict) -> RunScrap:
        data = FactorFileRunScrap(**{
            "taskId": runDto["taskId"],
            "taskUniqueId": runDto["taskId"] + str(uuid.uuid4())
        })
        return data
    

    def createProcessTask(self, runCrawling: MarcapRunScrap) -> ProcessTask:
        return ProcessTask(**{
            "market": "",
            "startDateStr": "20070101",
            "endDateStr": "20191231",
            "taskUniqueId": runCrawling.taskUniqueId,
            "taskId": runCrawling.taskId,
            "count": 1,
            "tasks": ["20070101~20191231"],
            "restCount": 1,
            "tasksRet": [0],
            "state": "find worker"
        })
    
    async def crawlingFactorsInFile(self):
        return await asyncio.create_task(self.factorRepository.getFactorsInFile())
    

    async def makeFactorLists(self, data: List[Dict]) -> List[FactorDao]:
        return await batchFunction(100, data, self.makeFactorList)
        
    
    async def makeFactorList(self, data: Dict):
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

    
    @eventsDecorator.on(FactorFileScraper.EVENT_FACTOR_FILE_ON_GET_FACTORS_INFILE)
    def getFactorsInFile(self, runCrawling: RunScrap):
        task = self.tasksRepository.getTask(runCrawling.taskId, runCrawling.taskUniqueId)
        task.state = "get factors in file"
        self.tasksRepository.updateTask(task)

    @eventsDecorator.on(FactorFileScraper.EVENT_FACTOR_FILE_ON_MAKE_FACTOR_DATA)
    def makeFactorData(self, runCrawling: RunScrap):
        task = self.tasksRepository.getTask(runCrawling.taskId, runCrawling.taskUniqueId)
        task.state = "make factor data"
        self.tasksRepository.updateTask(task)

    @eventsDecorator.on(FactorFileScraper.EVENT_FACTOR_FILE_ON_RESULT_OF_FACTOR)
    def onResultOfFactor(self, runCrawling: RunScrap, factorList: List):
        task = self.tasksRepository.getTask(runCrawling.taskId, runCrawling.taskUniqueId)
        task.state = "insert factor in db"

        async def completeMarcapTask() -> None:
            await self.factorRepository.insertFactor(factorList)
            self.tasksRepository.completeFactorConvertFileToDbTask(task, "all")
        asyncio.create_task(completeMarcapTask())
    

    
