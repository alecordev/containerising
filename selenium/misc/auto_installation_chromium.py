from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

try:
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # options.add_argument("--window-size=1920x1080")
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()))
    driver.get("https://www.google.com")
    driver.save_screenshot("auto_installation_chromium.png")
    driver.close()
    driver.quit()
except Exception as e:
    print(e)
