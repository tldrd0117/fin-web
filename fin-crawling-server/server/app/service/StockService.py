from typing import List
from app.repo.StockRepository import StockRepository
from app.model.dto import StockMarketCapital


class StockService:
    def __init__(self, stockRepository: StockRepository) -> None:
        self.stockRepository = stockRepository

    def getStockData(self, market: str, startDate: str, endDate: str) -> List[StockMarketCapital]:
        return self.stockRepository.getStockData(market, startDate, endDate)
    
