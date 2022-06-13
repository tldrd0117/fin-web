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
from app.model.scrap.model import SeibroStockNumRunScrap

# https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/company/BIP_CNTS01012V.xml&menuNo=53#

# 발행 주식 정보
class SeibroStockNumScraper(WebDriverScraper):
    EVENT_SEIBRO_STOCK_NUM_ON_CONNECTING_WEBDRIVER: Final = "SeibroStockNumScraper/onConnectingWebdriver"
    EVENT_SEIBRO_STOCK_NUM_ON_START_CRAWLING: Final = "SeibroStockNumScraper/onStartCrawling"
    EVENT_SEIBRO_STOCK_NUM_ON_END_CRAWLING: Final = "SeibroStockNumScraper/onEndCrawling"
    EVENT_SEIBRO_STOCK_NUM_ON_RESULT_OF_DATA: Final = "SeibroStockNumScraper/onResultOfData"

    def __init__(self, eventTarget) -> None:
        super().__init__(eventTarget)
        self.logger = Logger("SeibroStockNumScraper")

    async def crawling(self, dto: SeibroStockNumRunScrap) -> None:
        driver = None
        try:
            uuid = self.createUUID()
            await self.ee.emit(self.EVENT_SEIBRO_STOCK_NUM_ON_CONNECTING_WEBDRIVER, dto)
            driver: WebDriver = await asyncRetryNonBlock(5, 1, self.connectWebDriver, dto.driverAddr, uuid)
            for code in dto.codes:
                await self.ee.emit(self.EVENT_SEIBRO_STOCK_NUM_ON_START_CRAWLING, dto)
                data = await asyncRetryNonBlock(5, 1, self.crawlingOne, driver, code, dto.startDate, dto.endDate)
                await self.ee.emit(self.EVENT_SEIBRO_STOCK_NUM_ON_END_CRAWLING, dto)
                await self.ee.emit(self.EVENT_SEIBRO_STOCK_NUM_ON_RESULT_OF_DATA, dto, data)
                print(data)
        except Exception as e:
            print(traceback.format_exc())
            raise e
        finally:
            driver.quit()

    async def crawlingOne(self, driver: WebDriver, code: str, startDate: str, endDate:str) -> None:
        await sleepNonBlock(0.5)
        driver.get("https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/company/BIP_CNTS01012V.xml&menuNo=53#")
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.element_to_be_clickable((By.ID, "INPUT_SN2")))
        driver.execute_script(f'$("#INPUT_SN2").val("{code}")')
        driver.execute_script('$("#comN_image1").click()')
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.visibility_of_element_located((By.ID, "iframe1")))
        driver.switch_to_frame("iframe1")
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.presence_of_element_located((By.ID, "P_isinList_none")))
        await sleepNonBlock(1)
        isNone = driver.execute_script("return document.getElementById('P_isinList_none').style.display == 'none'")
        self.logger.info(isNone)
        if not isNone:
            return []
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.element_to_be_clickable((By.ID, "P_isinList_0_P_ISIN_ROW")))
        driver.execute_script('document.getElementById("P_isinList_0_P_ISIN_ROW").click()')
        driver.switch_to.default_content()
        driver.execute_script(f'$("#sd1_inputCalendar1_input").val("{startDate}")')
        driver.execute_script(f'$("#sd1_inputCalendar2_input").val("{endDate}")')
        driver.execute_script('$("#image12").click()')
        resultArr = []
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.invisibility_of_element((By.ID, "___processbar2")))
        driver.execute_script(f"$(\"*[alt='마지막 페이지'],*[alt='last page']\").click()")
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.invisibility_of_element((By.ID, "___processbar2")))
        size = driver.execute_script('return $(".w2pageList_label_selected").text()')
        if size == "":
            return []
        size = int(size)
        self.logger.info(f"changed! size:{str(size)}")
        driver.execute_script(f"$(\"*[alt='첫 페이지'],*[alt='first page']\").click()")
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.invisibility_of_element((By.ID, "___processbar2")))
        for index in range(1, size):
            await sleepNonBlock(0.5)
            data = await self.crawlingNextPage(driver, code)
            print(data)
            resultArr.append(data)
            driver.execute_script(f"$(\"*[alt='다음 페이지'],*[alt='next page']\").click()")
            WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.invisibility_of_element((By.ID, "___processbar2")))
        return resultArr
    
    async def crawlingNextPage(self, driver: WebDriver, code: str):
        html = driver.execute_script('return $("#grid1_body_table")[0].outerHTML')
        df: pd.DataFrame = pd.read_html(html)[0]
        df["발행일"] = df["발행일"].apply(lambda v : str(v).replace("/",""))
        df["상장일"] = df["상장일"].apply(lambda v : str(v).replace("/",""))
        df["code"] = code

        return df.to_dict("records")