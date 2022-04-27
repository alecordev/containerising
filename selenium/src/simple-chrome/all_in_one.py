import os
import io
import sys
import zipfile
import urllib.request
import tempfile
import pathlib

from selenium.webdriver.chrome.options import Options
from selenium import webdriver


def prep_chromium():
    try:
        url = "https://chromedriver.storage.googleapis.com/100.0.4896.60/chromedriver_linux64.zip"
        binary = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(url).read()))
        binary.extractall(tempfile.gettempdir())
        print(os.listdir(tempfile.gettempdir()))
        os.chmod(pathlib.Path(tempfile.gettempdir()).joinpath("chromedriver"), 755)

        print("Retrieved...")
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + tempfile.gettempdir()
    except Exception as e:
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + tempfile.gettempdir()
        print(e)


def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Enable if you don't want to see the UI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {
        "profile.default_content_settings": {"images": 2},
    }
    chrome_options.experimental_options["prefs"] = chrome_prefs
    # chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


if __name__ == "__main__":
    prep_chromium()
    driver = webdriver.Chrome(options=set_chrome_options())
    # Do stuff with your driver
    print("Chrome opened")
    driver.get("http://rugbychampagneweb.com")
    driver.save_screenshot("screenshot.png")
    driver.close()
