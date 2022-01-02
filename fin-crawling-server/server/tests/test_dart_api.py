from app.crawler.DartApiCrawler import DartApiCrawler
from app.model.dto import DartApiCrawling
import asyncio
import uuid


async def getCodes(dart: DartApiCrawler) -> None:
    #c211a43e6a9af3078ba60fc66708a51523a16bbf
    #48a43d39558cf752bc8d8e52709da34569a80372
    codes = await dart.downloadCodes(False, "c211a43e6a9af3078ba60fc66708a51523a16bbf")
    print(codes)


async def crawling(dart: DartApiCrawler) -> None:
    dto: DartApiCrawling = DartApiCrawling(**{
        "apiKey": "c211a43e6a9af3078ba60fc66708a51523a16bbf",
        "isCodeNew": False,
        "startYear": 2015,
        "endYear": 2015,
        "taskId": "factorDart",
        "taskUniqueId": str(uuid.uuid4())
    })
    result = await dart.crawling(dto)
    print(result)


# pytest -s test_dart_api.py
def test() -> None:
    loop = asyncio.get_event_loop()
    dart = DartApiCrawler()
    loop.run_until_complete(crawling(dart))
    loop.close()
