
from pymitter import EventEmitter

from .StockCrawlingRunCrawlingDTO import StockCrawlingRunCrawlingDTO
from .StockCrawlingTaskDTO import StockCrawlingTaskDTO
from .StockCrawlingTasksDTO import StockCrawlingTasksDTO
from .crawler.MarcapCrawler import MarcapCrawler
from .StockMarketCapitalResultDTO import StockMarketCapitalResultDTO


class StockCrawlingDataSource:
    def __init__(self, ee: EventEmitter) -> None:
        self.ee = ee
        self.tasks = StockCrawlingTasksDTO()

    def checkDoingCrawling(self) -> None:
        print("@@@###")
        print("checkDoingCrawling")
        self.ee.emit("crawlingService/updateTasks", self.tasks)

    def getStockData(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        task = StockCrawlingTaskDTO()
        crawler = MarcapCrawler.create(self.ee)
        crawler.crawling(dto)

        @self.ee.on("marcapCrawler/onConnectingWebdriver")
        def onConnectWebdriver() -> None:
            task.setTasks(dto.startDateStr, dto.endDateStr, dto.market, dto.taskId, dto.taskUniqueId)
            self.tasks.addTask(task)
            task.setState("connecting webdriver")
            self.tasks.updateTask(task)
            self.ee.emit("crawling/updateTasks", self.tasks)
        
        @self.ee.on("marcapCrawler/onStartCrawling")
        def onStartCrawling() -> None:
            task.setState("start crawling")
            self.tasks.updateTask(task)
            self.ee.emit("crawling/updateTasks", self.tasks)
            self.ee.emit("crawlingService/upsertTask", task)
        
        @self.ee.on("marcapCrawler/onDownloadStart")
        def onDownloadFile() -> None:
            task.setState("download file")
            self.tasks.updateTask(task)
            self.ee.emit("crawling/updateTasks", self.tasks)
            self.ee.emit("crawlingService/upsertTask", task)

        @self.ee.on("marcapCrawler/onDownloadComplete")
        def onDownloadComplete(isSuccess: bool) -> None:
            task.setState("download complete")
            self.tasks.updateTask(task)
            self.ee.emit("crawling/updateTasks", self.tasks)
            self.ee.emit("crawlingService/upsertTask", task)

        @self.ee.on("marcapCrawler/onParsingComplete")
        def onParsingComplete(isSuccess: bool, ret: StockMarketCapitalResultDTO) -> None:
            if isSuccess:
                task.success(1)
            else:
                task.fail(1)
            self.tasks.updateTask(task)
            self.ee.emit("crawling/updateTasks", self.tasks)
            self.ee.emit("crawlingService/upsertTask", task)
            self.ee.emit("crawlingService/upsertData", ret)

        @self.ee.on("marcapCrawler/onComplete")
        def onComplete() -> None:
            self.ee.emit("crawling/updateTasks", self.tasks)
            self.ee.emit("crawlingService/upsertTask", task)
            self.tasks.deleteTask(task)
            self.ee.emit("crawlingService/getCompletedTask")
