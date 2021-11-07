from typing import List
from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.model.dto import StockMarketCapital


class StockRepository(object):
    def __init__(self, mongod: StockMongoDataSource) -> None:
        super().__init__()
        self.mongod = mongod
    
    def getStockData(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
        return self.mongod.getMarcap(market, startDate, endDate)
    
    # def getFactor(self, market: str, startYear: str, endYear: str) -> List
    #     return self.mongod