from typing import Any, Dict
from typing_extensions import Final
from app.crawler.MarcapCrawler import EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, \
    EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, \
    EVENT_MARCAP_CRAWLING_ON_ERROR, \
    EVENT_MARCAP_CRAWLING_ON_CANCEL

from app.datasource.StockMongoDataSource import StockMongoDataSource
from app.model.dto import StockMarketCapitalResult, StockRunCrawling, StockCrawlingDownloadTask
from pymitter import EventEmitter
from app.repo.TasksRepository import TasksRepository
from app.module.logger import Logger


EVENT_TASK_REPO_UPDATE_TASKS = "taskRepo/updateTasks"
EVENT_TASK_REPO_TASK_COMPLETE = "taskRepo/completeTask"
EVENT_TASK_REPO_UPDATE_POOL_INFO = "taskRepo/updatePoolInfo"
EVENT_CRAWLING_REPO_ON_CRAWLING_COMPLETE: Final = "crawlingRepo/onCrawlingComplete"


class CrawlerRepository(object):
    def __init__(self, mongod: StockMongoDataSource, tasksRepository: TasksRepository) -> None:
        super().__init__()
        self.mongod = mongod
        self.ee = EventEmitter()
        self.logger = Logger("CrawlerRepository")
        self.tasksRepository = tasksRepository
        self.crawlers: Dict = dict()

    def createListener(self, ee: EventEmitter) -> None:
        ee.on(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, self.onConnectingWebDriver)
        ee.on(EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, self.onStartCrawling)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, self.onDownloadStart)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, self.onDownloadComplete)
        ee.on(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, self.onParsingComplete)
        ee.on(EVENT_MARCAP_CRAWLING_ON_ERROR, self.onError)
        ee.on(EVENT_MARCAP_CRAWLING_ON_CANCEL, self.onCancelled)
    
    # 크롤러 추가
    def addCrawler(self, uniqueId: str, crawler: Any) -> None:
        self.crawlers[uniqueId] = crawler
    
    # 크롤러 삭제
    def removeCrawler(self, uniqueId: str) -> None:
        del self.crawlers[uniqueId]
    
    # 크롤러 불러오기
    def getCrawlers(self) -> Dict:
        return self.crawlers
    
    # 하나의 크롤러 불러오기
    def getCrawler(self, uniqueId: str) -> Any:
        return self.crawlers[uniqueId]
    
    # 크롤링 중 웹드라이버와 연결되었을 때 이벤트
    def onConnectingWebDriver(self, dto: StockRunCrawling) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "connecting webdriver"
        self.tasksRepository.updateTask(task)
        self.logger.info("onConnectingWebDriver", task.taskUniqueId)

    # 크롤링이 시작되었을 떄 이벤트
    def onStartCrawling(self, dto: StockRunCrawling) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "start crawling"
        self.tasksRepository.updateTask(task)
        self.logger.info("onStartCrawling", task.taskUniqueId)
    
    # 크롤링 데이터 다운로드가 시작되었을 때 이벤트
    def onDownloadStart(self, dto: StockCrawlingDownloadTask) -> None:
        # self.logger.info("onDownloadStart: "+dto.json())
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download start"
        self.tasksRepository.updateTask(task)
        self.logger.info("onDownloadStart", task.taskUniqueId)

    # 크롤링 데이터 다운로드가 완료되었을 때 이벤트
    def onDownloadComplete(self, dto: StockCrawlingDownloadTask) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        task.state = "download complete"
        self.tasksRepository.updateTask(task)
        self.logger.info("onDownloadComplete", task.taskUniqueId)

    # 크롤링 데이터 변환이 완료되었을 때 이벤트
    def onParsingComplete(self, isSuccess: bool, retdto: StockMarketCapitalResult, dto: StockCrawlingDownloadTask) -> None:
        self.logger.info("onParsingComplete")
        self.logger.info(f"taskId:{dto.taskId} taskUniqueId{dto.taskUniqueId}")
        tar = self.tasksRepository.tasksdto.tasks[dto.taskId]["list"]
        self.logger.info(f"taskDTO: {tar}")
        self.tasksRepository.completeStockCrawlingTask(isSuccess, retdto, dto)
    
    # 크롤링이 취소되었을 때 이벤트
    def onCancelled(self, dto: StockRunCrawling) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        self.tasksRepository.fail(task, task.restCount)
        task.state = "cancelled"
        self.tasksRepository.updateTask(task)
        self.logger.info("onCancelled", task.taskUniqueId)
    
    # 크롤링이 에러가났을 때 이벤트
    def onError(self, dto: StockRunCrawling) -> None:
        task = self.tasksRepository.getTask(dto.taskId, dto.taskUniqueId)
        self.tasksRepository.fail(task, task.restCount)
        task.state = "error"
        self.tasksRepository.updateTask(task)
        self.logger.error("onError", task.taskUniqueId)
    
    

