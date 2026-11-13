# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "selenium==4.52.0",
# ]
# ///

import os
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

GRID_URL = os.environ.get("GRID_URL", "http://localhost:4444")


class PythonOrgSearch(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Remote(
            command_executor=GRID_URL, options=webdriver.FirefoxOptions()
        )

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("https://www.python.org")
        self.assertIn("Python", driver.title)
        elem = driver.find_element(By.NAME, "q")
        elem.send_keys("pycon")
        elem.send_keys(Keys.RETURN)
        assert "No results found." not in driver.page_source

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main()
