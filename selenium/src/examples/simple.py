# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

GRID_URL = os.environ.get("GRID_URL", "http://localhost:4444")

options = webdriver.ChromeOptions()
options.browser_version = "stable"  # optional; the Grid picks a matching node
driver = webdriver.Remote(command_executor=GRID_URL, options=options)
print("Session: " + driver.session_id)

try:
    driver.implicitly_wait(30)
    driver.set_window_size(1920, 1080)
    driver.get("https://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element(By.NAME, "q")
    elem.send_keys("documentation")
    elem.send_keys(Keys.RETURN)
    assert "No results found." not in driver.page_source
finally:
    driver.quit()
