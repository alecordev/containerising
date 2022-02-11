import time
import subprocess


def main():
    print(
        subprocess.run(
            'docker run -d -p 4444:4444 -p 7900:7900 --shm-size="2g" --name firefox-selenium selenium/standalone-firefox:4.1.2-20220131',
            shell=True
        )
    )
    try:
        print(f"Selenium started in ports 4444 (to use driver.Remote) and 7900 (for VNC)...")
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Detected keyboard interrupt, terminating gracefully...")
    finally:
        print(f"Cleaning up Docker containers...")
        print(subprocess.run("docker stop firefox-selenium", shell=True))
        print(subprocess.run("docker rm firefox-selenium", shell=True))


if __name__ == "__main__":
    main()
