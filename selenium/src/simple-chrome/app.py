import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

TARGET_URL = os.environ.get("TARGET_URL", "https://www.python.org")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")


def set_chrome_options() -> Options:
    """Headless Chrome options that work inside a container."""
    options = Options()
    if chrome_bin := os.environ.get("CHROME_BIN"):
        options.binary_location = chrome_bin
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )
    return options


def make_driver() -> webdriver.Chrome:
    # With CHROMEDRIVER_BIN unset, Selenium Manager finds/downloads a matching driver.
    driver_path = os.environ.get("CHROMEDRIVER_BIN")
    service = Service(executable_path=driver_path) if driver_path else Service()
    return webdriver.Chrome(service=service, options=set_chrome_options())


if __name__ == "__main__":
    driver = make_driver()
    try:
        driver.get(TARGET_URL)
        print(f"Title: {driver.title}")
        driver.save_screenshot(os.path.join(OUTPUT_DIR, "screenshot.png"))
    finally:
        driver.quit()
