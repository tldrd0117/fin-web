from app.scrap.base.WebDriverScraper import WebDriverScraper

# https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/company/BIP_CNTS01012V.xml&menuNo=53#

class SeibroStockNumCrawler(WebDriverScraper):
    async def crawling(self) -> None:
        pass