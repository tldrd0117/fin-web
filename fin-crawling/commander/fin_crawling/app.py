from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .observer.FileObserver import observe

def run():
    observer = observe()
    try:
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Remote(
            command_executor='http://webdriver:4444',
            options=chrome_options
        )
        driver.get("http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101")
        try:
            alert = WebDriverWait(driver, timeout=3).until(expected_conditions.alert_is_present())
            alert.accept()
        except:
            print("예외발생")

        before = ""
        # while len(before) <= 0:
        #     before = driver.execute_script("return $('.CI-MDI-UNIT-TIME').text()")
        #     driver.implicitly_wait(1)
        # after = before
        WebDriverWait(driver, timeout=10, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"#mktId_0_1")))
        # while before == after:
        #     driver.implicitly_wait(1)
        #     #코스피 선택

        before = driver.execute_script("return $('.CI-MDI-UNIT-TIME').text()")
        driver.execute_script('$("#mktId_0_1").click()')
        #     driver.implicitly_wait(1)
        driver.execute_script('$("#trdDd")[0].value = "20210104"')
        #     driver.implicitly_wait(1)
        driver.execute_script('$(".btn_component_search").click()')
        #     driver.implicitly_wait(1)
        after = before
        while before == after:
            after = driver.execute_script('return $(".CI-MDI-UNIT-TIME").text()')
            time.sleep(0.5)
        #     driver.implicitly_wait(1)
        print("before:"+before)
        print("after:"+after)
        WebDriverWait(driver, timeout=10, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"*[title='다운로드 팝업']")))
        driver.execute_script("$('[title=\"다운로드 팝업\"]').click()")
        WebDriverWait(driver, timeout=10, poll_frequency=1).until(EC.element_to_be_clickable((By.CSS_SELECTOR,"*[data-type='csv']")))
        driver.execute_script("$(\"[data-type='csv']\").click()")
        
        text = driver.execute_script('return $(".CI-GRID-BODY-TABLE tr").text()')
        time.sleep(3)
        # print(text)
        # table = tableElements[0]
        # print(table.text.split("\n"))
        driver.quit() 
    finally:
        observer.stop()
        observer.join()
