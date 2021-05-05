from fin_crawling import __version__
from fin_crawling.data.StockCrawlingDataSource import StockCrawlingDataSource
from fin_crawling.data.StockCrawlingRunCrawlingDTO import StockCrawlingRunCrawlingDTO
from pymitter import EventEmitter


# pytest -s
async def main() -> None:
    ee = EventEmitter()
    source = StockCrawlingDataSource(ee)
    dto = StockCrawlingRunCrawlingDTO.create('http://localhost:4444', "kospi", "20200316", "20210320", "marcap", "marcapkospi2020031620210320")
    await source.getStockData(dto)


def test() -> None:
    # asyncio.run(main())
    # service.runCrawling('http://localhost:4444', "20210316")
    # print("abcabc")
    pass


def test2() -> None:
    # dto = StockMarketCapitalResultDTO()
    # dto.data.append("hello")
    # print(dto.toDict())
    # print(dto.data)
    # print("complete")
    pass
    

def test_version() -> None:
    assert __version__ == '0.1.0'
