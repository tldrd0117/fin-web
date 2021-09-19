from __future__ import annotations
import asyncio
import os

from datetime import datetime, timedelta
from typing import TypeVar, Final
from asyncio.exceptions import CancelledError

from pymitter import EventEmitter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from watchdog.events import FileCreatedEvent
import uuid

from app.observer.DownloadObserver import DownloadObserver
from app.observer.CmdFileSystemEventHandler import FILE_SYSTEM_HANDLER

from pathlib import Path
from app.model.dto import StockCrawlingDownloadTask, StockCrawlingRunCrawling, StockMarketCapitalResult, StockMarketCapital
from uvicorn.config import logger

T = TypeVar("T")

EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER: Final = "marcapCrawler/onConnectingWebdriver"
EVENT_MARCAP_CRAWLING_ON_START_CRAWLING: Final = "marcapCrawler/onStartCrawling"
EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START: Final = "marcapCrawler/onDownloadStart"
EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE: Final = "marcapCrawler/onDownloadComplete"
EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE: Final = "marcapCrawler/onParsingComplete"
EVENT_MARCAP_CRAWLING_ON_CANCEL: Final = "marcapCrawler/cancel"
EVENT_MARCAP_CRAWLING_ON_ERROR: Final = "marcapCrawler/error"


class MarcapCrawler(object):
    
    def __init__(self) -> None:
        super().__init__()
        self.ee = EventEmitter()
        self.isLock = False
        self.isError = False

    def createUUID(self) -> str:
        return str(uuid.uuid4())

    def connectWebDriver(self, addr: str, uuid: str) -> WebDriver:
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            'profile.default_content_setting_values.automatic_downloads': 1,
            'download.default_directory': f"/home/seluser/Downloads/{uuid}"
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Remote(
            command_executor=addr,
            options=chrome_options,

        )
        driver.set_page_load_timeout(20)
        driver.set_script_timeout(20)
        return driver

    def connectLocalDriver(self, addr: str, uuid: str) -> WebDriver:
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            'profile.default_content_setting_values.automatic_downloads': 1,
            'download.default_directory': f"/Users/iseongjae/Documents/PersonalProjects/fin-web/fin-crawling-server/server/downloads/{uuid}"
        }
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(executable_path="/Users/iseongjae/Downloads/chromedriver", chrome_options=chrome_options)
        return driver

    async def crawling(self, dto: StockCrawlingRunCrawling) -> None:
        driver = None
        uuid = self.createUUID()
        logger.info(uuid)
        downloadObserver = None
        try:
            self.ee.emit(EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, dto)
            
            downloadObserver = DownloadObserver()
            path = await downloadObserver.makePath(uuid)
            downloadObserver.startObserver(path, self.ee)

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
                downloadTask = StockCrawlingDownloadTask(**{
                    "dateStr": dateStr,
                    "market": dto.market,
                    "uuid": uuid,
                    "taskId": dto.taskId,
                    "taskUniqueId": dto.taskUniqueId
                })
                print(downloadTask.json())
                downloadObserver.event_handler.setDownloadTask(downloadTask)
                self.ee.emit(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, downloadTask)
                await self.downloadData(downloadTask, downloadObserver, driver)
                date = date + timedelta(days=1)
        except CancelledError as ce:
            print(f"CancelledError: {str(ce)}")
            logger.error(f"CancelledError: {str(ce)}")
            self.ee.emit(EVENT_MARCAP_CRAWLING_ON_CANCEL, dto)
        except Exception as e:
            self.isError = True
            self.ee.emit(EVENT_MARCAP_CRAWLING_ON_ERROR, dto)
            print(f"error: {str(e)}")
            logger.error(f"error: {str(e)}")
        finally:
            if downloadObserver:
                downloadObserver.stopObserver()
            if driver:
                driver.quit()
    
    async def downloadData(self, downloadTask: StockCrawlingDownloadTask, downloadObserver: DownloadObserver, driver: WebDriver) -> None:
        logger.info("downloadData")
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
        logger.info("before:"+before)
        logger.info("after:"+after)
        await asyncio.sleep(3)
        WebDriverWait(driver, timeout=10, poll_frequency=2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "*[title='다운로드 팝업']")))
        driver.execute_script("$('[title=\"다운로드 팝업\"]').click()")
        WebDriverWait(driver, timeout=10, poll_frequency=2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "*[data-type='csv']")))
        driver.execute_script("$(\"[data-type='csv']\").click()")
        print("wait:"+downloadTask.dateStr)
        logger.info("wait:"+downloadTask.dateStr)
        self.isLock = True

        mainThreadLoop = asyncio.get_running_loop()

        @self.ee.once(FILE_SYSTEM_HANDLER(downloadTask.uuid))
        def downloadComplete(event: FileCreatedEvent, downloadTask: StockCrawlingDownloadTask) -> None:
            self.ee.emit(EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, downloadTask)
            mainThreadLoop.create_task(self.parseFile(event, downloadTask, downloadObserver))

        timeout = 30
        while self.isLock:
            timeout = timeout - 1
            if timeout <= 0:
                retdto = StockMarketCapitalResult()
                retdto.result = "fail"
                retdto.errorMsg = "timeout"
                self.ee.emit(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, False, retdto, downloadTask)
                return
            await asyncio.sleep(1, loop=mainThreadLoop)
            print(f"isLock:{str(self.isLock)} timeout:{timeout}")
            logger.info(f"isLock:{str(self.isLock)} timeout:{timeout}")
    
    def convertFileToDto(self, path: str, dto: StockMarketCapitalResult) -> None:
        lines = []
        with open(path, "r", encoding="utf-8") as f:
            p = Path(f.name)
            # dto.date = p.stem
            lines = f.readlines()
        
        for i in range(1, len(lines)):
            data = lines[i].replace('"', '').split(",")
            marcap = StockMarketCapital(**{
                "date": dto.date,
                "market": dto.market,
                "code": data[0].strip(),
                "name": data[1].strip(),
                "close": data[2].strip(),
                "diff": data[3].strip(),
                "percent": data[4].strip(),
                "open": data[5].strip(),
                "high": data[6].strip(),
                "low": data[7].strip(),
                "volume": data[8].strip(),
                "price": data[9].strip(),
                "marcap": data[10].strip(),
                "number": data[11].strip()
            })
            
            dto.data.append(marcap)

    async def isExistFile(self, path: str, ext: str = ".csv") -> bool:
        isExist = path.endswith(ext)
        restTimes = 3
        while not isExist and restTimes >= 0:
            await asyncio.sleep(1)
            isExist = path.endswith(ext)
            restTimes -= 1
        return isExist
    
    async def parseFile(self, event: FileCreatedEvent, downloadTask: StockCrawlingDownloadTask, downloadObserver: DownloadObserver) -> None:
        isSuccess = False
        retdto = StockMarketCapitalResult()
        try:
            date = downloadTask.dateStr
            market = downloadTask.market
            retdto.date = date
            retdto.market = market
            isExist = await self.isExistFile(event.src_path)
            if not isExist:
                return
            print("created: " + date)
            await asyncio.sleep(0.5)
            dest_path = f'{os.path.dirname(event.src_path)}/{market+"-"+date}.csv'
            if os.path.isfile(dest_path):
                return
            self.changeCharSet(event.src_path)
            os.rename(event.src_path, dest_path)
            self.convertFileToDto(dest_path, retdto)
            retdto.result = "success"
            isSuccess = True
            self.ee.emit(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, isSuccess, retdto, downloadTask)
            self.isLock = False
        except Exception as e:
            retdto.result = "fail"
            retdto.errorMsg = str(e)
            logger.error(str(e))
            self.ee.emit(EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, isSuccess, retdto, downloadTask)
            self.isLock = False
        finally:
            logger.info("parseFile...")

    def changeCharSet(self, path: str) -> None:
        lines = None
        with open(path, "r", encoding="euc-kr") as f:
            lines = f.readlines()
        with open(path, 'w', encoding="utf-8") as f:
            f.writelines(lines)

