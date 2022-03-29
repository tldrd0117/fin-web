from typing import List
from app.scrap.FactorDartScraper import FactorDartScraper
from app.model.scrap.model import FactorDartRunScrap
import asyncio
import uuid
from app.util.decorator import eventsDecorator
from dotenv import dotenv_values

config = dotenv_values('.env')


class EventsTest:
    def __init__(self) -> None:
        pass

    @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_DOWNLOADING_CODES)
    def onDownloadingCodes(self, dto: FactorDartRunScrap) -> None:
        print("FACTOR_DART_CRAWLER_ON_DOWNLOADING_CODES")
    
    @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_CRAWLING_FACTOR_DATA)
    def onCrawlingFactorData(self, dto: FactorDartRunScrap) -> None:
        print("FACTOR_DART_CRAWLER_ON_CRAWLING_FACTOR_DATA")
    
    @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_COMPLETE_YEAR)
    def onCompleteYear(self, dto: FactorDartRunScrap, year: int) -> None:
        print("FACTOR_DART_CRAWLER_ON_COMPLETE_YEAR")
        print(year)
    
    @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_RESULT_OF_FACTOR)
    def onResultOfFactor(self, dto: FactorDartRunScrap, year: int, obj: List) -> None:
        print("FACTOR_DART_CRAWLER_ON_RESULT_OF_FACTOR")
        print(obj)
        
    
    @eventsDecorator.on(FactorDartScraper.FACTOR_DART_CRAWLER_ON_CANCEL)
    def onCancel(self, dto: FactorDartRunScrap) -> None:
        print("FACTOR_DART_CRAWLER_ON_CANCEL")
        print(dto)


async def getCodes(dart: FactorDartScraper) -> None:
    codes = await dart.downloadCodes(False, config["apiKey"])
    print(codes)


async def crawling(dart: FactorDartScraper) -> None:
    dto: FactorDartRunScrap = FactorDartRunScrap(**{
        "apiKey": config["apiKey"],
        "isCodeNew": False,
        "startYear": 2021,
        "endYear": 2021,
        "taskId": "factorDart",
        "taskUniqueId": str(uuid.uuid4())
    })
    print(dto)
    eventsDecorator.register(EventsTest(), dart.ee)
    await dart.crawling(dto)


# pytest -s test_dart_api.py
def test() -> None:
    loop = asyncio.get_event_loop()
    dart = FactorDartScraper()
    loop.run_until_complete(crawling(dart))
    loop.close()
