import os
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class Scraper:
    """Minimal page scraper using headless Firefox."""

    def __init__(self) -> None:
        options = Options()
        if firefox_bin := os.environ.get("FIREFOX_BIN"):
            options.binary_location = firefox_bin
        options.add_argument("-headless")
        # Optional preferences (replace the removed FirefoxProfile / FirefoxBinary APIs):
        # options.set_preference("network.http.use-cache", False)
        # options.set_preference("general.useragent.override", "Mozilla/5.0 ...")
        self.driver = webdriver.Firefox(options=options)

    def scrape(self, link: str, wait: float = 2.0) -> str:
        self.driver.get(link)
        time.sleep(wait)  # let late JS settle
        self.driver.save_screenshot("screenshot.png")
        return self.driver.page_source

    def close(self) -> None:
        self.driver.quit()


if __name__ == "__main__":
    scraper = Scraper()
    try:
        html = scraper.scrape(os.environ.get("TARGET_URL", "https://www.python.org"))
        print(f"Fetched {len(html)} characters")
    finally:
        scraper.close()
