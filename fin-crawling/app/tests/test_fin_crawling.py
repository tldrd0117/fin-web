from fin_crawling import __version__
from fin_crawling.service.CrawlingService import CrawlingService
import asyncio
from datetime import timedelta, datetime

#pytest -s
async def main():
    service = CrawlingService()
    await service.runTaskCrawling('http://localhost:4444', "kospi","20200316", "20210320")

def test():
    asyncio.run(main())
    # service.runCrawling('http://localhost:4444', "20210316")
    print("abcabc")

def test_version():
    assert __version__ == '0.1.0'
