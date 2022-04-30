import asyncio
from app.util.AsyncUtil import asyncRetry
from app.scrap.SeibroDividendScraper import SeibroDividendScraper
from app.model.scrap.model import SeibroDividendRunScrap
import uuid
from cryptography.hazmat.primitives.asymmetric import rsa

async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    # rsa.generate_private_key()
    pass
    


# cd /Users/iseongjae/Documents/projects/fin-web/fin-crawling-server/server
# poetry run python -m pytest -s tests/test_saibro_dividend.py
def test() -> None:
    print("run test")
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()