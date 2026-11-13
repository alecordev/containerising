# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

"""Start a standalone Firefox Selenium container, keep it up until Ctrl+C, then clean up."""

import os
import subprocess
import time

IMAGE = os.environ.get("SELENIUM_IMAGE", "selenium/standalone-firefox:4.52.0")
NAME = "firefox-selenium"


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
    try:
        print("Selenium started on ports 4444 (webdriver.Remote) and 7900 (noVNC, password: secret)...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Detected keyboard interrupt, terminating gracefully...")
    finally:
        print("Cleaning up Docker containers...")
        # --rm removes the container as soon as it stops
        print(subprocess.run(["docker", "stop", NAME]))


if __name__ == "__main__":
    main()
