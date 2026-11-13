# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

import datetime
import random
import time

from selenium import webdriver


def log(msg) -> None:
    print(f"[{datetime.datetime.now(datetime.timezone.utc)}] {msg}")


def is_time() -> bool:
    """True between 08:00 and 21:00 UTC."""
    now = datetime.datetime.now(datetime.timezone.utc)
    log(now)
    return 8 < now.hour < 21


def make_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)


def main() -> None:
    while True:
        driver = None
        try:
            if is_time():
                driver = make_driver()
                driver.get("about:blank")
                driver.save_screenshot("about_blank.png")
        except Exception as e:
            log(f"Exception: {e}")
        finally:
            if driver is not None:
                driver.quit()
            ts = random.randint(5 * 60, 29 * 60)
            log(f"Waiting for {ts / 60:.1f} minutes.")
            time.sleep(ts)


if __name__ == "__main__":
    main()
