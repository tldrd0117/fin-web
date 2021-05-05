from __future__ import annotations
import asyncio
import os

from datetime import datetime, timedelta
from typing import TypeVar

from pymitter import EventEmitter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from watchdog.events import FileCreatedEvent

from fin_crawling.data.StockCrawlingDownloadTaskDTO import \
    StockCrawlingDownloadTaskDTO
from fin_crawling.data.StockCrawlingRunCrawlingDTO import \
    StockCrawlingRunCrawlingDTO
from fin_crawling.utils.FileUtil import changeCharSet
from fin_crawling.data.StockMarketCapitalResultDTO import StockMarketCapitalResultDTO

from .Crawler import Crawler

T = TypeVar("T")


class MarcapCrawler(Crawler[T]):
    @staticmethod
    def create(ee: EventEmitter) -> MarcapCrawler:
        crawler = MarcapCrawler[None]()
        crawler.ee = ee
        return crawler

    def connectWebDriver(self, addr: str) -> WebDriver:
        chrome_options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_setting_values.automatic_downloads': 1}
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Remote(
            command_executor=addr,
            options=chrome_options,
        )
        return driver

    async def crawling(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        driver = None
        self.ee.emit("marcapCrawler/onConnectingWebdriver")
        try:
            driver = self.connectWebDriver(dto.driverAddr)
            driver.get("http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101")
            try:
                alert = WebDriverWait(driver, timeout=3).until(EC.alert_is_present())
                alert.accept()
            except Exception as e:
                print("예외발생:"+str(e))
            print("start:"+dto.startDateStr)

            self.ee.emit("marcapCrawler/onStartCrawling")
            WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mktId_0_1")))
            date = datetime.strptime(dto.startDateStr, "%Y%m%d")
            endDate = datetime.strptime(dto.endDateStr, "%Y%m%d")

            while date <= endDate:
                dateStr = date.strftime("%Y%m%d")
                self.ee.emit("marcapCrawler/onDownloadStart")
                downloadTask = StockCrawlingDownloadTaskDTO(dateStr, dto.market, self.ee)
                await asyncio.create_task(self.downloadData(downloadTask, driver))
                date = date + timedelta(days=1)
        except Exception as e:
            print(f"error: {str(e)}")
        finally:
            if driver:
                driver.quit()
    
    async def downloadData(self, downloadTask: StockCrawlingDownloadTaskDTO, driver: WebDriver) -> None:
        if driver is None:
            return
        # pymitter
        before = driver.execute_script("return $('.CI-MDI-UNIT-TIME').text()")
        if downloadTask.market == "kospi":
            driver.execute_script('$("#mktId_0_1").click()')
        elif downloadTask.market == "kosdaq":
            driver.execute_script('$("#mktId_0_2").click()')
        elif downloadTask.market == "konex":
            driver.execute_script('$("#mktId_0_3").click()')
        #     driver.implicitly_wait(1)
        driver.execute_script(f'$("#trdDd")[0].value = "{downloadTask.dateStr}"')
        #     driver.implicitly_wait(1)
        driver.execute_script('$(".btn_component_search").click()')
        #     driver.implicitly_wait(1)
        after = before
        while before == after:
            after = driver.execute_script('return $(".CI-MDI-UNIT-TIME").text()')
            await asyncio.sleep(0.5)
        #     driver.implicitly_wait(1)
        print("before:"+before)
        print("after:"+after)
        await asyncio.sleep(3)
        WebDriverWait(driver, timeout=10, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "*[title='다운로드 팝업']")))
        driver.execute_script("$('[title=\"다운로드 팝업\"]').click()")
        WebDriverWait(driver, timeout=10, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "*[data-type='csv']")))
        driver.execute_script("$(\"[data-type='csv']\").click()")
        print("wait:"+downloadTask.dateStr)
        self.isLock = True
        
        @self.ee.on("observer/downloadComplete")
        def downloadComplete(event: FileCreatedEvent, downloadTask: StockCrawlingDownloadTaskDTO) -> None:
            self.isLock = False
            self.ee.emit("marcapCrawler/onDownloadComplete")
            self.parseFile(event, downloadTask)

        while self.isLock:
            await asyncio.sleep(1)
            print(f"isLock:{str(self.isLock)}")

    async def parseFile(self, event: FileCreatedEvent, downloadTask: StockCrawlingDownloadTaskDTO) -> None:
        isSuccess = False
        ret = StockMarketCapitalResultDTO()
        try:
            date = downloadTask.dateStr
            market = downloadTask.market
            if not event.src_path.endswith(".csv"):
                await asyncio.sleep(1)
                name = os.path.basename(event.src_path).split(".")[0]
                if not os.path.exists(os.path.dirname(event.src_path)+name+".csv"):
                    ret.result = "fail"
                    raise Exception('')
            print("created: " + date)

            dest_path = f'{os.path.dirname(event.src_path)}/{date}.csv'
            await asyncio.sleep(0.5)
            changeCharSet(event.src_path)
            os.rename(event.src_path, dest_path)

            ret.readData(dest_path, market)
            ret.result = "success"
            isSuccess = True
        except Exception as e:
            print(e)
            ret.result = "fail"
        finally:
            downloadTask.stopObserver()
            self.ee.emit("marcapCrawler/onParsingComplete", isSuccess, ret)
