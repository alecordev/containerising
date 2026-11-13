# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

"""Fill in and submit a login form. Credentials come from the environment, never the source."""

import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

LOGIN_URL = os.environ.get("LOGIN_URL", "https://the-internet.herokuapp.com/login")
USERNAME = os.environ.get("LOGIN_USERNAME", "tomsmith")
PASSWORD = os.environ.get("LOGIN_PASSWORD", "SuperSecretPassword!")  # public demo site

options = Options()
# options.add_argument("-headless")
browser = webdriver.Firefox(options=options)

try:
    browser.get(LOGIN_URL)
    browser.find_element(By.ID, "username").send_keys(USERNAME)
    browser.find_element(By.ID, "password").send_keys(PASSWORD)
    browser.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    WebDriverWait(browser, 10).until(EC.url_contains("/secure"))
    print(browser.title)
finally:
    browser.quit()
