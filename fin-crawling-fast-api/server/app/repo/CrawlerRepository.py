from app.crawler.MarcapCrawler import marcapCrawler, ee, \
    EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, \
    EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_START_CRAWLING
from app.model.dto import StockCrawlingRunCrawlingDTO, StockMarketCapitalResultDTO


class CrawlerRepository(object):

    def getMarcapData(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        marcapCrawler.crawling(dto)

        @ee.on(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER)
        def onConnectingWebDriver(dto: StockCrawlingRunCrawlingDTO) -> None:
            pass

        @ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE)
        def onDownloadComplete() -> None:
            pass

        @ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START)
        def onDownloadStart() -> None:
            pass

        @ee.on(EVENT_MARCAP_CRAWLING_ON_START_CRAWLING)
        def onStartCrawling() -> None:
            pass

        @ee.on(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE)
        def onParsingComplete(isSuccess: bool, retdto: StockMarketCapitalResultDTO) -> None:
            pass

