from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..observer.FileObserver import observe
import time
import asyncio
from datetime import timedelta, datetime
import queue
import os
from ..utils.FileUtil import changeCharSet
from .StockCrawlingTaskDTO import StockCrawlingTaskDTO

class StockCrawlingDataSource:
    def __init__(self):
        pass
    async def getStockData(self, driverAddr, index, startDateStr, endDateStr, ee):
        self.currentTask = StockCrawlingTaskDTO()
        self.currentTask.setTasks(startDateStr, endDateStr)
        observer, event_handler = observe()
        driver = None
        try:
            chrome_options = webdriver.ChromeOptions()
            prefs = {'profile.default_content_setting_values.automatic_downloads': 1}
            chrome_options.add_experimental_option("prefs", prefs)
            driver = webdriver.Remote(
                command_executor=driverAddr,
                options=chrome_options
            )
            # driver = webdriver.Chrome('/Users/iseongjae/Downloads/chromedriver2', options=chrome_options)
            
            driver.get("http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101")
            try:
                alert = WebDriverWait(driver, timeout=3).until(expected_conditions.alert_is_present())
                alert.accept()
            except:
                print("예외발생")
            print("start:"+startDateStr)
            before = ""
            # while len(before) <= 0:
            #     before = driver.execute_script("return $('.CI-MDI-UNIT-TIME').text()")
            #     driver.implicitly_wait(1)
            # after = before
            WebDriverWait(driver, timeout=10, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#mktId_0_1")))
            # while before == after:
            #     driver.implicitly_wait(1)
            #     #코스피 선택

            date = datetime.strptime(startDateStr,"%Y%m%d")
            endDate = datetime.strptime(endDateStr,"%Y%m%d")

            while date <= endDate:
                dateStr = date.strftime("%Y%m%d")
                print("date:"+dateStr)
                task = asyncio.create_task(self.downloadData(driver, index, dateStr, event_handler))
                ret = await task
                if ret == "success":
                    self.currentTask.success(1)
                else:
                    self.currentTask.fail(1)
                ee.emit("taskComplete",self.currentTask)
                print(ret)
                print(self.currentTask)
                date = date + timedelta(days=1)
                print(date, endDate)
        finally:
            observer.stop()
            observer.join()
            if driver:
                driver.quit()
            ee.emit("crawlingComplete", self.currentTask)
        
    async def downloadData(self, driver, index, dateStr, event_handler):
        ##pymitter
        self.queue = queue.Queue()
        self.completeQueue = queue.Queue()
        event_handler.setQueue(self.queue)
        event_handler.setCreatedCallback(self.processStockFile)
        before = driver.execute_script("return $('.CI-MDI-UNIT-TIME').text()")
        if index == "kospi":
            driver.execute_script('$("#mktId_0_1").click()')
        elif index == "kosdaq":
            driver.execute_script('$("#mktId_0_2").click()')
        elif index == "konex":
            driver.execute_script('$("#mktId_0_3").click()')
        #     driver.implicitly_wait(1)
        driver.execute_script(f'$("#trdDd")[0].value = "{dateStr}"')
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
        WebDriverWait(driver, timeout=10, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"*[title='다운로드 팝업']")))
        driver.execute_script("$('[title=\"다운로드 팝업\"]').click()")
        WebDriverWait(driver, timeout=10, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"*[data-type='csv']")))
        driver.execute_script("$(\"[data-type='csv']\").click()")
        self.queue.put_nowait(dateStr)
        print("wait:"+dateStr)
        text = driver.execute_script('return $("#trdDd")[0].value')
        self.queue.join()
        ret = self.completeQueue.get()
        self.completeQueue.task_done()
        return ret
    
    async def processStockFile(self, event):
        if not event.src_path.endswith(".csv"):
            await asyncio.sleep(1)
            name = os.path.basename(event.src_path).split(".")[0]
            if not os.path.exists(os.path.dirname(event.src_path)+name+".csv"):
                self.completeQueue.put_nowait("fail")
                self.queue.task_done()
        data = self.queue.get()
        print("created: " + data)
        dest_path = f'{os.path.dirname(event.src_path)}/{data}.csv'
        print(event.src_path)
        print(dest_path)
        await asyncio.sleep(0.5)
        changeCharSet(event.src_path)
        os.rename(event.src_path, dest_path)
        self.completeQueue.put_nowait("success")
        self.queue.task_done()

    
