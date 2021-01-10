from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def run():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
        command_executor='http://webdriver:4444',
        options=chrome_options
    )
    driver.get("http://marketdata.krx.co.kr/contents/MKD/04/0404/04040200/MKD04040200.jsp")
    before = driver.execute_script('return $(".func-icon-time span").text()')
    after = before
    while before == after:
        driver.implicitly_wait(1)
        driver.execute_script('$("form > dl:nth-child(1) > dd > input")[1].click()')
        driver.implicitly_wait(1)
        driver.execute_script("$('form > dl:nth-child(8) input')[0].value = 20210104")
        driver.implicitly_wait(1)
        driver.execute_script('$("form button")[1].click()')
        driver.implicitly_wait(1)
        after = driver.execute_script('return $(".func-icon-time span").text()')
        driver.implicitly_wait(1)
        print(before)
        print(after)

    text = driver.execute_script('return $(".CI-GRID-BODY-TABLE tr").text()')
    print(text)
    # table = tableElements[0]
    # print(table.text.split("\n"))
    driver.quit() 