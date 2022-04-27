import time
import random
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def log(msg):
    timestamp = datetime.datetime.utcnow()
    print(f"[{timestamp}] {msg}")


def is_time():
    now = datetime.datetime.utcnow()
    log(now)
    if 21 > now.hour > 8:
        return True
    return False


def main():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--window-size=1920x1080")
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    while 1:
        try:
            if is_time():
                driver.get('about:blank')
                driver.save_screenshot('about_blank.png')
        except Exception as e:
            log(f"Exception: {e}")
        finally:
            driver.close()
            driver.quit()
            ts = random.randint(5 * 60, 29 * 60)
            log(f"Waiting for {ts/60} minutes.")
            time.sleep(ts)


if __name__ == '__main__':
    main()
