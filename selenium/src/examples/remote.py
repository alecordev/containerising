# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

"""Selenium 4: pass browser Options (desired_capabilities was removed) to webdriver.Remote."""

import os

from selenium import webdriver

GRID_URL = os.environ.get("GRID_URL", "http://localhost:4444")

for options in (
    webdriver.ChromeOptions(),
    webdriver.FirefoxOptions(),
    webdriver.EdgeOptions(),  # needs the edge node: docker compose --profile edge up -d
):
    try:
        driver = webdriver.Remote(command_executor=GRID_URL, options=options)
    except Exception as e:
        print(f"{options.browser_name}: not available ({type(e).__name__})")
        continue
    try:
        driver.get("https://www.python.org")
        print(f"{options.browser_name}: {driver.title}")
    finally:
        driver.quit()
