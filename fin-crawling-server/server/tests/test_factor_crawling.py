from app.crawler.FactorCrawler import FactorCrawler
from app.model.dto import FactorRunCrawling


# pytest -s test_factor_crawling.py
def test():
    factorCrawler = FactorCrawler()
    factorCrawler.crawling(FactorRunCrawling(**{
        "market": "kospi",
        "year": "2018"
    }))

