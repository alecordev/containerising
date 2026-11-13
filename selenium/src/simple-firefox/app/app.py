import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

TARGET_URL = os.environ.get("TARGET_URL", "https://www.python.org")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")


def make_driver() -> webdriver.Firefox:
    options = Options()
    if firefox_bin := os.environ.get("FIREFOX_BIN"):
        options.binary_location = firefox_bin
    options.add_argument("-headless")
    return webdriver.Firefox(options=options)


if __name__ == "__main__":
    driver = make_driver()
    try:
        driver.get(TARGET_URL)
        print(f"Title: {driver.title}")
        driver.save_screenshot(os.path.join(OUTPUT_DIR, "screenshot.png"))
    finally:
        driver.quit()
