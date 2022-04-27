import time
import subprocess
from selenium import webdriver


def main():
    cmd = subprocess.run(
            'docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" --name firefox-selenium selenium/standalone-firefox:4.1.2-20220131',
            shell=True,
        )
    print(cmd)
    driver = webdriver.Remote(command_executor="http://localhost:4444")

    try:
        driver.implicitly_wait(30)
        driver.maximize_window()
        driver.get("http://www.python.org")
        assert "Python" in driver.title
        driver.get("http://rugbychampagneweb.com")
        time.sleep(5)
        driver.get("http://artswit.com")
        time.sleep(10)
    finally:
        driver.quit()
        cmd = subprocess.run("docker stop firefox-selenium", shell=True)
        print(cmd)
        cmd = subprocess.run("docker rm firefox-selenium", shell=True)
        print(cmd)


if __name__ == "__main__":
    main()
