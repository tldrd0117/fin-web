from pymitter import EventEmitter
from app.crawler.MarcapCrawler import MarcapCrawler
from app.model.dto import StockRunCrawling, StockCrawlingDownloadTask, StockMarketCapitalResult
import asyncio
import os
from app.crawler.MarcapCrawler import EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, \
    EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, \
    EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, \
    EVENT_MARCAP_CRAWLING_ON_ERROR, \
    EVENT_MARCAP_CRAWLING_ON_CANCEL


def createListener(ee: EventEmitter) -> None:
    @ee.on(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER)
    def onConnectingWebDriver(dto: StockRunCrawling) -> None:
        print("onConnectingWebDriver")
        print(dto)

    @ee.on(EVENT_MARCAP_CRAWLING_ON_START_CRAWLING)
    def onStartCrawling(dto: StockRunCrawling) -> None:
        print("onStartCrawling")
        print(dto)

    @ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START)
    def onDownloadStart(dto: StockCrawlingDownloadTask) -> None:
        print("onDownloadStart")
        print(dto)

    @ee.on(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE)
    def onDownloadComplete(dto: StockCrawlingDownloadTask) -> None:
        print("onDownloadComplete")
        print(dto)

    @ee.on(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE)
    def onParsingComplete(isSuccess: bool, retdto: StockMarketCapitalResult, dto: StockCrawlingDownloadTask) -> None:
        print("onParsingComplete")
        print(dto)

    @ee.on(EVENT_MARCAP_CRAWLING_ON_CANCEL)
    def onCancelled(dto: StockRunCrawling) -> None:
        print("onCancelled")
        print(dto)

    @ee.on(EVENT_MARCAP_CRAWLING_ON_ERROR)
    def onError(dto: StockRunCrawling) -> None:
        print("onError")
        print(dto)


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    print("runTest")
    runDto = StockRunCrawling(**{
        "driverAddr": "http://localhost:30006",
        "market": "kospi",
        "startDateStr": "20210826",
        "endDateStr": "20210827",
        "taskId": "marcap",
        "taskUniqueId": "99883377"
    })
    print("create marcapCrawler")
    marcapCrawler = MarcapCrawler()
    createListener(marcapCrawler.ee)
    print("task")
    await loop.create_task(marcapCrawler.crawling(runDto))


# pytest -s test_marcap_crawler_local.py
def test() -> None:
    loop = asyncio.get_event_loop()
    print("create_task")
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()