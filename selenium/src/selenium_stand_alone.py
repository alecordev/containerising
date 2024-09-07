import time
import datetime
import subprocess

from selenium import webdriver


def now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def log(msg):
    print(f"[{now().isoformat()}] {msg}")


def main():
    cmd = subprocess.run(
        'docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" --name firefox-selenium selenium/standalone-firefox:latest',
        shell=True,
    )
    log(cmd)
    log("Waiting for the container to start... (5 seconds)...")
    time.sleep(5)

    driver = type("Driver", (), {"quit": lambda self: None})()

    try:
        from selenium.webdriver.firefox.options import Options

        firefox_options = Options()
        # firefox_options.add_argument("--headless")  # Run in headless mode (important for Docker)
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        # firefox_options.add_argument("--window-size=1920,1080")
        # firefox_options.add_argument("--start-maximized")
        driver = webdriver.Remote(
            command_executor="http://localhost:4444", options=firefox_options
        )

        log("Starting...")
        driver.set_window_size(1920, 1080)
        driver.implicitly_wait(30)
        driver.maximize_window()
        driver.get("http://www.python.org")
        assert "Python" in driver.title
        driver.save_screenshot("python.png")
        driver.get("http://rugbychampagneweb.com")
        time.sleep(5)
        driver.save_screenshot("rugbychampagneweb.png")
        driver.get("http://artswit.com")
        time.sleep(10)
        driver.save_screenshot("artswit.png")
    except Exception as e:
        log(e)
    else:
        log("Success - No errors")
    finally:
        driver.quit()
        cmd = subprocess.run("docker stop firefox-selenium", shell=True)
        log(cmd)
        cmd = subprocess.run("docker rm firefox-selenium", shell=True)
        log(cmd)


if __name__ == "__main__":
    main()
