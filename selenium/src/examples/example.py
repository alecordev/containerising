# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

"""Use a Grid / standalone container that is already running (see ../../docker-compose*.yml)."""

import os
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

GRID_URL = os.environ.get("GRID_URL", "http://localhost:4444")


def main() -> None:
    driver = webdriver.Remote(command_executor=GRID_URL, options=Options())
    try:
        driver.implicitly_wait(30)
        driver.maximize_window()
        driver.get("https://www.python.org")
        assert "Python" in driver.title
        driver.get("https://example.com")
        time.sleep(2)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
