import asyncio

from watchdog.events import FileCreatedEvent


class CrawlingService:
    stockCrawlingDataSource = StockCrawlingDataSource(ee)
    stockMongoDataSource = StockMongoDataSource()

    def runCrawling(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        if dto.taskId == "marcap":
            asyncio.run(stockCrawlingDataSource.getStockData(dto))

    def checkDoingCrawling() -> None:
        stockCrawlingDataSource.checkDoingCrawling()
    
    def getCompletedTask() -> None:
        data = stockMongoDataSource.selectCompleteTask()
        ee.emit("crawling/updateTaskHistory", data, False)
    

    def updateData(result: StockMarketCapitalResultDTO) -> None:
        stockMongoDataSource.insertMarcap(result.data)
    

    def upsertTask(task: StockCrawlingTaskDTO) -> None:
        stockMongoDataSource.upsertTask(task.toDict())
    

    def downloadComplete(event: FileCreatedEvent, downloadTask: StockCrawlingDownloadTaskDTO) -> None:
        asyncio.run(stockCrawlingDataSource.processStockFile(event, downloadTask))
