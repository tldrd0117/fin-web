from typing import List
from app.repo.StockRepository import StockRepository
from app.repo.TasksRepository import TasksRepository
from app.repo.CrawlerRepository import CrawlerRepository
from app.scrap.MarcapScraper import MarcapScraper
from app.service.scrap.base.ScrapService import ScrapService
from app.model.dto import StockMarketCapital, \
    StockMarketCapitalResult, StockCrawlingDownloadTask, ProcessTask

from app.model.scrap.model import MarcapRunScrap, RunScrap

from app.module.task import Pool, Task, TaskPool
from app.module.logger import Logger

import asyncio
from datetime import datetime, timedelta
from collections import deque
import traceback
from app.base.BaseComponent import BaseComponent


class StockApiService(ScrapService):
    
    def onComponentResisted(self) -> None:
        self.stockRepository: StockRepository = self.get(StockRepository)
        self.tasksRepository: TasksRepository = self.get(TasksRepository)
        self.crawlerRepository: CrawlerRepository = self.get(CrawlerRepository)
        self.logger = Logger("StockService")
        return super().onComponentResisted()


    async def getStockData(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
        return await self.stockRepository.getStockData(market, startDate, endDate)

    
    async def getStockCodes(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
        data = await self.stockRepository.getStockData(market, startDate, endDate)