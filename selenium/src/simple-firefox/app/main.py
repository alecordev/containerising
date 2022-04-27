import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

# FireFox binary path (Must be absolute path)
FIREFOX_BINARY = FirefoxBinary("/opt/firefox/firefox")

# FireFox PROFILE
# PROFILE = webdriver.FirefoxProfile()
# PROFILE.set_preference("browser.cache.disk.enable", False)
# PROFILE.set_preference("browser.cache.memory.enable", False)
# PROFILE.set_preference("browser.cache.offline.enable", False)
# PROFILE.set_preference("network.http.use-cache", False)
# PROFILE.set_preference(
#     "general.useragent.override",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:72.0) Gecko/20100101 Firefox/72.0",
# )

# FireFox Options
# FIREFOX_OPTS = Options()
# FIREFOX_OPTS.log.level = "trace"  # Debug
# FIREFOX_OPTS.headless = True
# GECKODRIVER_LOG = "/geckodriver.log"


class Scraper:
    def __init__(self):
        self.driver = webdriver.Firefox(firefox_binary=FIREFOX_BINARY)

    def scrape(self, link):
        try:
            self.driver.get(link)
            time.sleep(5)  # just in case
            html = self.driver.page_source
            self.driver.save_screenshot('Screenshot.png')
            return html
        except Exception as e:
            print(e)


if __name__ == '__main__':
    pretty_html = Scraper().scrape("http://rugbychampagneweb.com").prettify()
