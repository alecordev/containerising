from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait

options = Options()
options.binary_location = "/opt/firefox/firefox"
service = Service(executable_path="/usr/bin/")
browser = webdriver.Firefox(options=options)
try:
    browser.get("http://www.facebook.com")

    username = browser.find_element(value="email")
    password = browser.find_element(value="pass")
    submit = browser.find_element(value="loginbutton")
    username.send_keys("YOUR EMAILID")
    password.send_keys("YOUR PASSWORD")

    submit.click()

    wait = WebDriverWait(browser, 5)
    page_title = browser.title
    assert page_title == "Facebook"
    print(page_title)
except Exception as e:
    print(e)
finally:
    browser.close()
