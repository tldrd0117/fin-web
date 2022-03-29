import asyncio
from app.util.AsyncUtil import asyncRetry
from app.scrap.SeibroDividendScraper import SeibroDividendScraper
from app.model.scrap.model import SeibroDividendRunScrap
import uuid


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    try:
        runDto: SeibroDividendRunScrap = SeibroDividendRunScrap(**{
            "driverAddr": "http://localhost:30006",
            "startDate": "20180101",
            "endDate": "20190101",
            "codes": ["005930"],
            "taskId":"test_saibro",
            "taskUniqueId": str(uuid.uuid4())
        })
        seibro = SeibroDividendScraper()
        await seibro.crawling(runDto)
        
    except Exception as e:
        print("error!")
        print(e)


# pytest -s test_saibro.py
def test() -> None:
    print("run test")
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()