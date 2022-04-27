from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

try:
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
    driver.get("https://www.google.com")
    driver.save_screenshot("auto_installation_firefox.png")
    driver.close()
    driver.quit()
except Exception as e:
    print(e)
