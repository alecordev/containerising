# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

"""Drive Chromium instead of Chrome; Selenium Manager still resolves the matching chromedriver."""

import shutil

from selenium import webdriver

options = webdriver.ChromeOptions()
# Point at the Chromium binary (e.g. /usr/bin/chromium on Debian/Ubuntu)
options.binary_location = shutil.which("chromium") or shutil.which("chromium-browser") or ""
# options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)
try:
    driver.get("https://www.python.org")
    driver.save_screenshot("auto_installation_chromium.png")
finally:
    driver.quit()
