import asyncio
import traceback
from typing import Dict
from typing_extensions import Final

from numpy import dtype
from app.scrap.base.WebDriverScraper import WebDriverScraper
from app.util.AsyncUtil import asyncRetry, asyncRetryNonBlock, sleepNonBlock
from selenium.webdriver.remote.webdriver import WebDriver
from app.module.logger import Logger
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import pandas as pd
from app.model.scrap.model import SeibroDividendRunScrap

# https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/company/BIP_CNTS01041V.xml&menuNo=285


class SeibroDividendScraper(WebDriverScraper):
    EVENT_SEIBRO_DIVIDEND_ON_CONNECTING_WEBDRIVER: Final = "SeibroDividendScraper/onConnectingWebdriver"
    EVENT_SEIBRO_DIVIDEND_ON_START_CRAWLING: Final = "SeibroDividendScraper/onStartCrawling"
    EVENT_SEIBRO_DIVIDEND_ON_END_CRAWLING: Final = "SeibroDividendScraper/onEndCrawling"
    EVENT_SEIBRO_DIVIDEND_ON_RESULT_OF_DATA: Final = "SeibroDividendScraper/onResultOfData"
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logger("MarcapCrawler")
    

    async def crawling(self, dto: SeibroDividendRunScrap) -> None:
        driver = None
        try:
            uuid = self.createUUID()
            await self.ee.emit(self.EVENT_SEIBRO_DIVIDEND_ON_CONNECTING_WEBDRIVER, dto)
            driver: WebDriver = await asyncRetryNonBlock(5, 1, self.connectWebDriver, dto.driverAddr, uuid)
            for code in dto.codes:
                await self.ee.emit(self.EVENT_SEIBRO_DIVIDEND_ON_START_CRAWLING, dto)
                data = await asyncRetryNonBlock(5, 1, self.crawlingOne, driver, code, dto.startDate, dto.endDate)
                await self.ee.emit(self.EVENT_SEIBRO_DIVIDEND_ON_END_CRAWLING, dto)
                await self.ee.emit(self.EVENT_SEIBRO_DIVIDEND_ON_RESULT_OF_DATA, dto, data)
        except Exception as e:
            print(traceback.format_exc())
            raise e
        finally:
            driver.quit()

    async def crawlingOne(self, driver: WebDriver, code: str, startDate: str, endDate:str) -> None:
        await sleepNonBlock(0.5)
        driver.get("https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/company/BIP_CNTS01041V.xml&menuNo=285")
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.element_to_be_clickable((By.ID, "Com_ISIN_input_0")))
        driver.execute_script('$("#Com_ISIN_input_0").val("종목")')
        driver.execute_script(f'$("#INPUT_SN2").val("{code}")')
        driver.execute_script('$("#cc_image1").click()')
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.visibility_of_element_located((By.ID, "iframe1")))
        driver.switch_to_frame("iframe1")
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.presence_of_element_located((By.ID, "P_isinList_none")))
        await sleepNonBlock(1)
        isNone = driver.execute_script("return document.getElementById('P_isinList_none').style.display == 'none'")
        self.logger.info(isNone)
        if not isNone:
            return None
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.element_to_be_clickable((By.ID, "P_isinList_0_P_ISIN_ROW")))
        driver.execute_script('document.getElementById("P_isinList_0_P_ISIN_ROW").click()')
        driver.switch_to.default_content()
        driver.execute_script(f'$("#inputCalendar1_input").val("{startDate}")')
        driver.execute_script(f'$("#inputCalendar2_input").val("{endDate}")')
        driver.execute_script('$("#image1").click()')
        resultArr = []
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.invisibility_of_element((By.ID, "___processbar2")))
        driver.execute_script(f"$(\"*[alt='마지막 페이지'],*[alt='last page']\").click()")
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.invisibility_of_element((By.ID, "___processbar2")))
        size = driver.execute_script('return $(".w2pageList_label_selected").text()')
        size = int(size)
        self.logger.info(f"changed! size:{str(size)}")
        driver.execute_script(f"$(\"*[alt='첫 페이지'],*[alt='first page']\").click()")
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.invisibility_of_element((By.ID, "___processbar2")))
        for index in range(1, size):
            await sleepNonBlock(0.5)
            data = await self.crawlingNextPage(driver)
            resultArr.append(data)
            driver.execute_script(f"$(\"*[alt='다음 페이지'],*[alt='next page']\").click()")
            WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.invisibility_of_element((By.ID, "___processbar2")))
        return resultArr
    
    async def crawlingNextPage(self, driver: WebDriver):
        html = driver.execute_script('return $("#grid1_body_table")[0].outerHTML')
        df: pd.DataFrame = pd.read_html(html, converters={('종목코드', '종목코드'):str})[0]
        df.columns = list(map(lambda c: c[0], df.columns))
        return df.to_dict("records")

