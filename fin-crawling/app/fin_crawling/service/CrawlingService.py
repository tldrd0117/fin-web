import asyncio

from watchdog.events import FileCreatedEvent

from fin_crawling.data.StockCrawlingDataSource import StockCrawlingDataSource
from fin_crawling.data.StockCrawlingDownloadTaskDTO import \
    StockCrawlingDownloadTaskDTO
from fin_crawling.data.StockCrawlingRunCrawlingDTO import \
    StockCrawlingRunCrawlingDTO
from fin_crawling.data.StockMongoDataSource import StockMongoDataSource
from fin_crawling.data.StockCrawlingTaskDTO import StockCrawlingTaskDTO
from fin_crawling.data.StockMarketCapitalResultDTO import StockMarketCapitalResultDTO
from fin_crawling.utils.EventEmitterWrapper import ee


def setupCrawlingService() -> None:
    stockCrawlingDataSource = StockCrawlingDataSource(ee)
    stockMongoDataSource = StockMongoDataSource()

    @ee.on("crawlingService/runCrawling")
    def runCrawling(dto: StockCrawlingRunCrawlingDTO) -> None:
        if dto.taskId == "marcap":
            asyncio.run(stockCrawlingDataSource.getStockData(dto))

    @ee.on("crawlingService/checkDoingCrawling")
    def checkDoingCrawling() -> None:
        stockCrawlingDataSource.checkDoingCrawling()

    @ee.on("crawlingService/getCompletedTask")
    def getCompletedTask() -> None:
        data = stockMongoDataSource.selectCompleteTask()
        ee.emit("crawling/updateTaskHistory", data, False)

    @ee.on("crawlingService/updateData")
    def updateData(result: StockMarketCapitalResultDTO) -> None:
        stockMongoDataSource.insertMarcap(result.data)

    @ee.on("crawlingService/upsertTask")
    def upsertTask(task: StockCrawlingTaskDTO) -> None:
        stockMongoDataSource.upsertTask(task.toDict())

    @ee.on("crawlingService/downloadComplete")
    def downloadComplete(event: FileCreatedEvent, downloadTask: StockCrawlingDownloadTaskDTO) -> None:
        asyncio.run(stockCrawlingDataSource.processStockFile(event, downloadTask))
