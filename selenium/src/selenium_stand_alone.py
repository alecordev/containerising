# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

import datetime
import json
import os
import subprocess
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

IMAGE = os.environ.get("SELENIUM_IMAGE", "selenium/standalone-firefox:4.52.0")
NAME = "firefox-selenium"
GRID_URL = os.environ.get("GRID_URL", "http://localhost:4444")


def now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def log(msg) -> None:
    print(f"[{now().isoformat()}] {msg}")


def wait_for_grid(url: str, timeout: float = 90.0) -> None:
    """Poll the Grid /status endpoint until it reports ready."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{url}/status", timeout=2) as resp:
                if json.load(resp).get("value", {}).get("ready"):
                    return
        except OSError:
            pass
        time.sleep(1)
    raise TimeoutError(f"Selenium Grid at {url} was not ready after {timeout:.0f}s")


def main() -> None:
    log(
        subprocess.run(
            [
                "docker", "run", "-d", "--rm",
                "-p", "4444:4444", "-p", "7900:7900",
                "--shm-size=2g", "--name", NAME, IMAGE,
            ],
            check=True,
        )
    )
    driver = None
    try:
        log("Waiting for the Grid to be ready...")
        wait_for_grid(GRID_URL)

        options = Options()
        # options.add_argument("-headless")  # the container already has a virtual display
        driver = webdriver.Remote(command_executor=GRID_URL, options=options)

        log("Starting...")
        driver.set_window_size(1920, 1080)
        driver.implicitly_wait(30)
        driver.get("https://www.python.org")
        assert "Python" in driver.title
        driver.save_screenshot("python.png")
        driver.get("https://example.com")
        driver.save_screenshot("example.png")
    except Exception as e:
        log(f"Error: {e!r}")
    else:
        log("Success - No errors")
    finally:
        if driver is not None:
            driver.quit()
        log(subprocess.run(["docker", "stop", NAME]))


if __name__ == "__main__":
    main()
