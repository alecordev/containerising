# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

options = FirefoxOptions()
options.add_argument("-headless")  # Firefox uses a single dash
driver = webdriver.Firefox(options=options)
try:
    driver.get("https://www.python.org")
    print(driver.title)
finally:
    driver.quit()
