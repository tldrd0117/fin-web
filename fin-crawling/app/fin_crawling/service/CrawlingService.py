import asyncio
from ..data.StockCrawlingDataSource import StockCrawlingDataSource
from pymitter import EventEmitter

class CrawlingService:
    def __init__(self):
        self.stockCrawlingDataSource = StockCrawlingDataSource()
        self.ee = EventEmitter()

    def runCrawling(self, driverAddr, index, startDateStr, endDateStr, ee):
        asyncio.run(self.runTaskCrawling(driverAddr, index, startDateStr, endDateStr, ee))

    async def runTaskCrawling(self, driverAddr, index, startDateStr, endDateStr, ee):
        task = asyncio.create_task(self.stockCrawlingDataSource.getStockData(driverAddr, index, startDateStr, endDateStr, ee))
        await task
    

    

    
    