from app.crawler.DartApiCrawler import DartApiCrawler
from app.model.dto import DartApiCrawling
import asyncio


async def getCodes(dart: DartApiCrawler) -> None:
    codes = await dart.downloadCodes(True, "48a43d39558cf752bc8d8e52709da34569a80372")
    print(codes)


async def crawling(dart: DartApiCrawler) -> None:
    dto: DartApiCrawling = DartApiCrawling(**{
        "apiKey": "48a43d39558cf752bc8d8e52709da34569a80372",
        "isCodeNew": False,
        "startYear": 2015,
        "endYear": 2015
    })
    result = await dart.crawling(dto)
    print(result)


# pytest -s test_dart_api.py
def test() -> None:
    loop = asyncio.get_event_loop()
    dart = DartApiCrawler()
    loop.run_until_complete(crawling(dart))
    loop.close()
