from selenium.webdriver.chrome.options import Options
from selenium import webdriver


def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {
        "profile.default_content_settings": {"images": 2},
    }
    chrome_options.experimental_options["prefs"] = chrome_prefs
    # chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


if __name__ == "__main__":
    driver = webdriver.Chrome(options=set_chrome_options())
    # Do stuff with your driver
    print("Chrome opened")
    driver.get("http://rugbychampagneweb.com")
    driver.save_screenshot("screenshot.png")
    driver.close()
