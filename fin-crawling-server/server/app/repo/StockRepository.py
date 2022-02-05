from typing import List
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.model.dto import StockMarketCapital, StockMarketCapitalResult
from pymitter import EventEmitter
from app.repo.TasksRepository import TasksRepository
from app.module.logger import Logger


class StockRepository(object):
    def __init__(self, mongod: StockMongoDataSource, tasksRepository: TasksRepository) -> None:
        super().__init__()
        self.mongod = mongod
        self.tasksRepository = tasksRepository
        self.logger = Logger("StockRepository")
        self.ee = EventEmitter()

    # db의 주식 시가총액 데이터를 반환한다.
    async def getStockData(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
        return await self.mongod.getMarcap(market, startDate, endDate)

    async def insertMarcap(self, dto: StockMarketCapitalResult) -> None:
        await self.mongod.insertMarcap(dto.data)
