# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

"""Start a standalone Firefox Selenium container, use it, and always clean it up."""

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
    print(
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
        wait_for_grid(GRID_URL)
        driver = webdriver.Remote(command_executor=GRID_URL, options=Options())
        driver.implicitly_wait(30)
        driver.maximize_window()
        driver.get("https://www.python.org")
        assert "Python" in driver.title
        print(f"Title: {driver.title}")
    finally:
        if driver is not None:
            driver.quit()
        print(subprocess.run(["docker", "stop", NAME]))


if __name__ == "__main__":
    main()
