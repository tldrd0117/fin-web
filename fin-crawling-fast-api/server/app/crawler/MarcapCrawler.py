from __future__ import annotations
import asyncio
import os

from datetime import datetime, timedelta
from typing import TypeVar, Final

from pymitter import EventEmitter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from watchdog.events import FileCreatedEvent
import uuid

from app.observer.DownloadObserver import DownloadObserver
from app.observer.CmdFileSystemEventHandler import FILE_SYSTEM_HANDLER

from .Crawler import Crawler
from pathlib import Path
from app.model.dto import StockCrawlingDownloadTaskDTO, StockCrawlingRunCrawlingDTO, StockCrawlingTaskDTO, StockMarketCapitalResultDTO, StockMarketCapitalDTO

T = TypeVar("T")

EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER: Final = "marcapCrawler/onConnectingWebdriver"
EVENT_MARCAP_CRAWLING_ON_START_CRAWLING: Final = "marcapCrawler/onStartCrawling"
EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START: Final = "marcapCrawler/onDownloadStart"
EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE: Final = "marcapCrawler/onDownloadComplete"
EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE: Final = "marcapCrawler/onParsingComplete"


class MarcapCrawler(Crawler[T]):
    @staticmethod
    def create(ee: EventEmitter) -> MarcapCrawler:
        crawler = MarcapCrawler[None]()
        crawler.ee = EventEmitter()
        return crawler

    def createUUID(self) -> str:
        return str(uuid.uuid4())

    def connectWebDriver(self, addr: str, uuid: str) -> WebDriver:
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            'profile.default_content_setting_values.automatic_downloads': 1,
            'download.default_directory': f"/usr/src/downloads/{uuid}"
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Remote(
            command_executor=addr,
            options=chrome_options,
        )
        return driver

    async def crawling(self, dto: StockCrawlingRunCrawlingDTO) -> None:
        driver = None
        uuid = self.createUUID()
        self.ee.emit(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, dto)
        try:
            driver = self.connectWebDriver(dto.driverAddr, uuid)
            driver.get("http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101")
            try:
                alert = WebDriverWait(driver, timeout=3).until(EC.alert_is_present())
                alert.accept()
            except Exception as e:
                print("예외발생:"+str(e))
            print("start:"+dto.startDateStr)

            self.ee.emit(EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, dto)
            WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mktId_0_1")))
            date = datetime.strptime(dto.startDateStr, "%Y%m%d")
            endDate = datetime.strptime(dto.endDateStr, "%Y%m%d")

            while date <= endDate:
                dateStr = date.strftime("%Y%m%d")
                downloadTask = StockCrawlingDownloadTaskDTO(**{
                    "dateStr": dateStr,
                    "market": dto.market,
                    "uuid": uuid,
                    "taskId": dto.taskId,
                    "taskUniqueId": dto.taskUniqueId
                })
                self.ee.emit(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, downloadTask)
                downloadObserver = DownloadObserver()
                downloadObserver.startObserver(uuid, self.ee)
                await self.downloadData(downloadTask, downloadObserver, driver)
                date = date + timedelta(days=1)
        except Exception as e:
            print(f"error: {str(e)}")
        finally:
            if driver:
                driver.quit()
    
    async def downloadData(self, downloadTask: StockCrawlingDownloadTaskDTO, downloadObserver: DownloadObserver, driver: WebDriver) -> None:
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

        @self.ee.on(FILE_SYSTEM_HANDLER(downloadTask.uuid))
        def downloadComplete(event: FileCreatedEvent, downloadTask: StockCrawlingDownloadTaskDTO) -> None:
            self.isLock = False
            self.ee.emit(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, downloadTask)
            self.parseFile(event, downloadTask, downloadObserver)

        while self.isLock:
            await asyncio.sleep(1)
            print(f"isLock:{str(self.isLock)}")
    
    def convertFileToDto(self, path: str, dto: StockMarketCapitalResultDTO) -> None:
        lines = []
        with open(path, "r", encoding="utf-8") as f:
            p = Path(f.name)
            dto.date = p.stem
            lines = f.readlines()
        
        for i in range(1, len(lines)):
            marcap = StockMarketCapitalDTO()
            data = lines[i].replace('"', '').split(",")
            marcap.date = dto.date
            marcap.market = dto.market
            marcap.code = data[0].strip()
            marcap.name = data[1].strip()
            marcap.close = data[2].strip()
            marcap.diff = data[3].strip()
            marcap.percent = data[4].strip()
            marcap.open = data[5].strip()
            marcap.high = data[6].strip()
            marcap.low = data[7].strip()
            marcap.volume = data[8].strip()
            marcap.price = data[9].strip()
            marcap.marcap = data[10].strip()
            marcap.number = data[11].strip()
            marcap.createdAt = datetime.today()
            marcap.updatedAt = ""
            dto.data.append(marcap)

    async def isExistFile(self, path: str, ext: str = ".csv") -> bool:
        isExist = path.endswith(ext)
        restTimes = 3
        while not isExist and restTimes >= 0:
            await asyncio.sleep(1)
            isExist = path.endswith(ext)
            restTimes -= 1
        return isExist
    
    async def parseFile(self, event: FileCreatedEvent, downloadTask: StockCrawlingDownloadTaskDTO, downloadObserver: DownloadObserver) -> None:
        isSuccess = False
        retdto = StockMarketCapitalResultDTO()
        try:
            date = downloadTask.dateStr
            market = downloadTask.market
            retdto.date = date
            retdto.market = market
            isExist = await self.isExistFile(event.src_path)
            if not isExist:
                raise Exception('file Not Exist')
            print("created: " + date)
            await asyncio.sleep(0.5)
            dest_path = f'{os.path.dirname(event.src_path)}/{date}.csv'
            self.changeCharSet(event.src_path)
            os.rename(event.src_path, dest_path)
            self.convertFileToDto(dest_path, retdto)
            retdto.result = "success"
            isSuccess = True
        except Exception as e:
            retdto.result = "fail"
            retdto.errorMsg = str(e)
        finally:
            downloadObserver.stopObserver()
            self.ee.emit(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, isSuccess, retdto, downloadTask)

    def changeCharSet(self, path: str) -> None:
        lines = None
        with open(path, "r", encoding="euc-kr") as f:
            lines = f.readlines()
        with open(path, 'w', encoding="utf-8") as f:
            f.writelines(lines)


ee = EventEmitter()
marcapCrawler: MarcapCrawler = MarcapCrawler(ee)
