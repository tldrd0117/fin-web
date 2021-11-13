from typing import List
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.model.dto import StockMarketCapital, StockMarketCapitalResult
from pymitter import EventEmitter

from app.crawler.MarcapCrawler import EVENT_MARCAP_CRAWLING_ON_RESULT_OF_STOCK_DATA


class StockRepository(object):
    def __init__(self, mongod: StockMongoDataSource) -> None:
        super().__init__()
        self.mongod = mongod

    def createListners(self, ee: EventEmitter) -> None:
        ee.on(EVENT_MARCAP_CRAWLING_ON_RESULT_OF_STOCK_DATA, self.onResultOfStockData)
    
    def onResultOfStockData(self, dto: StockMarketCapitalResult) -> None:
        self.mongod.insertMarcap(dto.data)
    
    def getStockData(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
        return self.mongod.getMarcap(market, startDate, endDate)
    
    # def getFactor(self, market: str, startYear: str, endYear: str) -> List
    #     return self.mongod