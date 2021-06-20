from typing import Final
from app.crawler.MarcapCrawler import EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, \
    EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_START_CRAWLING
from app.model.dto import StockCrawlingDownloadTaskDTO, StockCrawlingRunCrawlingDTO, StockMarketCapitalResultDTO
from app.datasource.StockMongoDataSource import mongod
from pymitter import EventEmitter
from uvicorn.config import logger


EVENT_CRAWLING_REPO_ON_CRAWLING_COMPLETE: Final = "crawlingRepo/onCrawlingComplete"


class CrawlerRepository(object):
    def __init__(self) -> None:
        super().__init__()

    def createListener(self, ee: EventEmitter) -> None:
        ee.on(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, self.onConnectingWebDriver)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, self.onDownloadComplete)
        ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, self.onDownloadStart)
        ee.on(EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, self.onStartCrawling)
        ee.on(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, self.onParsingComplete)
    
    def onConnectingWebDriver(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        pass

    def onDownloadComplete(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        pass

    def onDownloadStart(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        pass

    def onStartCrawling(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        pass

    def onParsingComplete(self, isSuccess: bool, retdto: StockMarketCapitalResultDTO, dto: StockCrawlingDownloadTaskDTO) -> None:
        # logger.info("mongod:"+retdto.json())
        mongod.insertMarcap(retdto.dict())
    
    

