# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

"""Selenium Manager (built into selenium >= 4.6) installs the driver automatically."""

from selenium import webdriver

options = webdriver.ChromeOptions()
# options.add_argument("--headless=new")
# options.add_argument("--no-sandbox")
# options.add_argument("--window-size=1920,1080")
# options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
try:
    driver.get("https://www.python.org")
    driver.save_screenshot("auto_installation_chrome.png")
finally:
    driver.quit()
