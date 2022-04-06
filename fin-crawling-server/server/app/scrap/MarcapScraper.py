from __future__ import annotations
import asyncio
import os
import traceback

from datetime import datetime, timedelta
from typing import Dict, List, TypeVar
from typing_extensions import Final

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import uuid

from app.observer.DownloadObserver import DownloadObserver
from app.observer.CmdFileSystemEventHandler import FILE_SYSTEM_HANDLER
from app.module.logger import Logger
from app.util.AsyncUtil import asyncRetry, asyncRetryNonBlock, sleepNonBlock
from app.scrap.base.WebDriverScraper import WebDriverScraper

# from pathlib import Path
from app.model.dto import StockCrawlingDownloadTask, StockRunCrawling, StockMarketCapitalResult, StockMarketCapital

T = TypeVar("T")


class MarcapScraper(WebDriverScraper):
    EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER: Final ="MarcapScraper/onConnectingWebdriver"
    EVENT_MARCAP_CRAWLING_ON_START_CRAWLING: Final ="MarcapScraper/onStartCrawling"
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START: Final ="MarcapScraper/onDownloadStart"
    EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE: Final ="MarcapScraper/onDownloadComplete"
    EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE: Final ="MarcapScraper/onParsingComplete"
    EVENT_MARCAP_CRAWLING_ON_RESULT_OF_STOCK_DATA: Final ="MarcapScraper/onResultOfStockData"
    
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logger("MarcapScraper")


    async def goKrxMarcapPage(self, driver: WebDriver) -> None:
        driver.get("http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101")
        try:
            alert = WebDriverWait(driver, timeout=3).until(EC.alert_is_present())
            alert.accept()
        except Exception as e:
            print("예외발생:"+str(e))
        WebDriverWait(driver, timeout=20, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#mktId_0_1")))

    async def crawling(self, dto: StockRunCrawling) -> None:
        driver = None
        downloadObserver = None
        try:
            uuid = self.createUUID()
            self.logger.info("crawling", uuid)
            await self.ee.emit(self.EVENT_MARCAP_CRAWLING_ON_CONNECTING_WEBDRIVER, dto)
            
            downloadObserver = DownloadObserver()
            path = await asyncRetryNonBlock(5, 1, downloadObserver.makePath, uuid)
            downloadObserver.startObserver(path, self.ee)
            self.logger.info("crawling", "create observer and start")
            print("startObserver")

            driver: WebDriver = await asyncRetryNonBlock(5, 1, self.connectWebDriver, dto.driverAddr, uuid)
            print("connectWebDriver")
            await self.ee.emit(self.EVENT_MARCAP_CRAWLING_ON_START_CRAWLING, dto)


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
                self.logger.info("crawling", f"create downloadTask taskId: {dto.taskId} market: {dto.market} date: {dateStr} taskUniqueId: {dto.taskUniqueId}")
                print(downloadTask.json())
                downloadObserver.event_handler.setDownloadTask(downloadTask)
                await self.ee.emit(self.EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_START, downloadTask)
                await asyncRetryNonBlock(5, 1, self.downloadData, downloadTask, downloadObserver, driver)
                # await self.downloadData(downloadTask, downloadObserver, driver)
                date = date + timedelta(days=1)
        except Exception as e:
            raise e
        finally:
            if downloadObserver:
                downloadObserver.stopObserver()
            if driver:
                driver.quit()
    
    async def downloadData(self, downloadTask: StockCrawlingDownloadTask, downloadObserver: DownloadObserver, driver: WebDriver) -> None:
        self.logger.info("downloadData")
        if driver is None:
            return
        beforeFilesLength = await self.getCompletedDownloadFileLength(downloadTask.uuid, driver)
        self.logger.info(f"beforeLength: {beforeFilesLength}")
        await self.goKrxMarcapPage(driver)
        
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
            await sleepNonBlock(0.5)
        #     driver.implicitly_wait(1)
        print("before:"+before)
        print("after:"+after)
        await sleepNonBlock(3)
        WebDriverWait(driver, timeout=10, poll_frequency=2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "*[class='CI-MDI-UNIT-DOWNLOAD']")))
        driver.execute_script("$('[class=\"CI-MDI-UNIT-DOWNLOAD\"]').click()")
        WebDriverWait(driver, timeout=10, poll_frequency=2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "*[data-type='csv']")))
        driver.execute_script("$(\"[data-type='csv']\").click()")
        print("wait:"+downloadTask.dateStr)
        await sleepNonBlock(3)

        # queue: asyncio.Queue = asyncio.Queue(maxsize=1, loop=loop)
        isWaiting = True
        timeout = 0
        print(str(isWaiting))
        print(str(timeout))
        self.logger.info(str(isWaiting))
        self.logger.info(str(timeout))
        while isWaiting and timeout < 30:
            afterFiles = await asyncio.create_task(self.getCompletedDownloadFile(downloadTask.uuid, driver))
            afterFilesLength = len(afterFiles)
            print(f"timeout: {timeout} afterFileLength: {afterFilesLength}")
            self.logger.info(f"afterFileLength: {afterFilesLength}")
            if afterFilesLength > 0 and beforeFilesLength != afterFilesLength:
                await self.ee.emit(self.EVENT_MARCAP_CRAWLING_ON_DOWNLOAD_COMPLETE, downloadTask)
                await asyncRetryNonBlock(3, 1, self.parseReceivedFile, afterFiles[0], downloadTask)
                # await asyncio.create_task(self.makeMarcapData(afterFiles[0], downloadTask))
                isWaiting = False
                break
            timeout = timeout + 1
            await sleepNonBlock(1)
        
        if isWaiting:
            raise Exception("timeout")


    def convertFileToDto(self, path: str, dto: StockMarketCapitalResult) -> None:
        lines = []
        with open(path, "r", encoding="utf-8") as f:
            # p = Path(f.name)
            # dto.date = p.stem
            lines = f.readlines()
        
        for i in range(1, len(lines)):
            data = lines[i].replace('"', '').split(",")
            if dto.market == "kospi":
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
            else:
                marcap = StockMarketCapital(**{
                    "date": dto.date,
                    "market": dto.market,
                    "code": data[0].strip(),
                    "name": data[1].strip(),
                    "close": data[3].strip(),
                    "diff": data[4].strip(),
                    "percent": data[5].strip(),
                    "open": data[6].strip(),
                    "high": data[7].strip(),
                    "low": data[8].strip(),
                    "volume": data[9].strip(),
                    "price": data[10].strip(),
                    "marcap": data[11].strip(),
                    "number": data[12].strip()
                })
            # print("append marcap: " + str(marcap))
            
            dto.data.append(marcap)

    async def isExistFile(self, path: str, ext: str = ".csv") -> bool:
        isExist = False
        restTimes = 3
        while not isExist and restTimes >= 0:
            await sleepNonBlock(1)
            isExist = path.endswith(ext)
            isExist = isExist and os.path.isfile(path)
            restTimes -= 1
        return isExist
    
    async def parseReceivedFile(self, path: str, downloadTask: StockCrawlingDownloadTask) -> None:
        retdto = StockMarketCapitalResult()
        date = downloadTask.dateStr
        market = downloadTask.market
        retdto.date = date
        retdto.market = market
        isExist = await self.isExistFile(path)
        if not isExist:
            return
        print("created: " + date)
        await sleepNonBlock(0.5)
        dest_path = f'{os.path.dirname(path)}/{market+"-"+date}.csv'
        if os.path.isfile(dest_path):
            return
        self.changeCharSet(path)
        os.rename(path, dest_path)
        self.convertFileToDto(dest_path, retdto)
        retdto.result = "success"
        await self.ee.emit(self.EVENT_MARCAP_CRAWLING_ON_PARSING_COMPLETE, True, retdto, downloadTask)
        await self.ee.emit(self.EVENT_MARCAP_CRAWLING_ON_RESULT_OF_STOCK_DATA, downloadTask, retdto)
        self.logger.info("parseFile", f"success, {downloadTask.taskUniqueId}")
    

    def changeCharSet(self, path: str) -> None:
        lines = None
        with open(path, "r", encoding="euc-kr") as f:
            lines = f.readlines()
        with open(path, 'w', encoding="utf-8") as f:
            f.writelines(lines)

