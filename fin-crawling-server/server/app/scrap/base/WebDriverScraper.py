from typing import List
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import asyncio
from app.scrap.base.Scraper import Scraper


class WebDriverScraper(Scraper):
    
    def createUUID(self) -> str:
        return str(uuid.uuid4())

    async def connectWebDriver(self, addr: str, uuid: str) -> WebDriver:
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
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
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

    async def getCompletedDownloadFile(self, uuid: str, driver: WebDriver) -> List:
        # driver.get("chrome://downloads/")
        # return driver.execute_script( \
        #     "return downloads.Manager.get().items_   "
        #     "  .filter(e => e.state === 'COMPLETE')  "
        #     "  .map(e => e.filePath || e.file_path); " )
        # return driver.execute_script("return document.querySelector('downloads-manager')"+
        #     ".shadowRoot.querySelector('#downloadsList')"+         
        #     ".items.filter(e => e.state === 'COMPLETE')"+          
        #     ".map(e => e.filePath || e.file_path || e.fileUrl || e.file_url)")
        driver.get(f"file:///home/seluser/Downloads/{uuid}")
        return driver.execute_script(f"return Array.prototype.slice.call(document.querySelectorAll('.icon.file')).map(v=>'/usr/src/downloads/{uuid}/'+v.text)")
    
    async def getCompletedDownloadFileLength(self, uuid: str, driver: WebDriver) -> int:
        files = await self.getCompletedDownloadFile(uuid, driver)
        print(str(files))
        return len(files)