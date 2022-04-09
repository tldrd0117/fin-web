import asyncio
from app.util.AsyncUtil import asyncRetry
from app.scrap.SeibroStockNumScraper import SeibroStockNumScraper
from app.model.scrap.model import SeibroStockNumRunScrap
import uuid


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    try:
        runDto: SeibroStockNumRunScrap = SeibroStockNumRunScrap(**{
            "driverAddr": "http://localhost:30006",
            "startDate": "19700101",
            "endDate": "20190101",
            "codes": ["001067"],
            "taskId":"test_saibro",
            "taskUniqueId": str(uuid.uuid4())
        })
        seibro = SeibroStockNumScraper()
        await seibro.crawling(runDto)
        
    except Exception as e:
        print("error!")
        print(e)


# cd /Users/iseongjae/Documents/projects/fin-web/fin-crawling-server/server
# poetry run python -m pytest -s tests/test_saibro_stock_num.py
def test() -> None:
    print("run test")
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()