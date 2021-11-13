
from typing import List
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.module.logger import Logger
from pymitter import EventEmitter
from app.crawler.FactorCrawler import EVENT_FACTOR_CRAWLING_ON_RESULT_OF_FACTOR


class FactorRepository(object):
    def __init__(self, mongod: StockMongoDataSource) -> None:
        super().__init__()
        self.mongod = mongod
        self.logger = Logger("FactorRepository")
    
    def createListners(self, ee: EventEmitter) -> None:
        ee.on(EVENT_FACTOR_CRAWLING_ON_RESULT_OF_FACTOR, self.onResultOfFactor)
    
    def onResultOfFactor(self, result: List) -> None:
        pass
        