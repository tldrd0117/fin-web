from selenium import webdriver
from selenium.webdriver.common.by import By

def run():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Remote(
        command_executor='http://webdriver:4444',
        options=chrome_options
    )
    driver.get("http://www.google.com")
    element = driver.find_element(By.ID, "SIvCob")
    print(element.text)
    driver.quit() 