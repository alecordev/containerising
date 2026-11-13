"""Run Chrome locally with no Docker and no manual driver download.

Selenium Manager (bundled with selenium >= 4.6) resolves the right chromedriver
(and Chrome for Testing if Chrome is missing) automatically.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def set_chrome_options() -> Options:
    options = Options()
    # options.add_argument("--headless=new")  # enable if you do not want to see the UI
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option(
        "prefs", {"profile.managed_default_content_settings.images": 2}
    )
    return options


if __name__ == "__main__":
    driver = webdriver.Chrome(options=set_chrome_options())
    try:
        driver.get("https://www.python.org")
        print(f"Title: {driver.title}")
        driver.save_screenshot("screenshot.png")
    finally:
        driver.quit()
