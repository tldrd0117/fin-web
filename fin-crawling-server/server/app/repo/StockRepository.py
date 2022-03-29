from typing import List
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.model.dto import StockMarketCapital, StockMarketCapitalResult
from pymitter import EventEmitter
from app.repo.TasksRepository import TasksRepository
from app.module.logger import Logger
from app.base.BaseComponent import BaseComponent


class StockRepository(BaseComponent):
    
    def onComponentResisted(self) -> None:
        self.mongod: StockMongoDataSource = self.get(StockMongoDataSource)
        self.tasksRepository = self.get(TasksRepository)
        self.logger = Logger("StockRepository")
        self.ee = EventEmitter()
        return super().onComponentResisted()

    # db의 주식 시가총액 데이터를 반환한다.
    async def getStockData(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
        return await self.mongod.getMarcap(market, startDate, endDate)

    async def getMarcapCodes(self, startDate: str, endDate: str) -> List[str]:
        return await self.mongod.getMarcapCodes(startDate, endDate)

    async def insertMarcap(self, dto: StockMarketCapitalResult) -> None:
        await self.mongod.insertMarcap(dto.data)
