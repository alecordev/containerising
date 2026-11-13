# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

"""Selenium Manager downloads geckodriver automatically."""

from selenium import webdriver

options = webdriver.FirefoxOptions()
# options.add_argument("-headless")

driver = webdriver.Firefox(options=options)
try:
    driver.get("https://www.python.org")
    driver.save_screenshot("auto_installation_firefox.png")
finally:
    driver.quit()
