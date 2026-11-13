# Selenium

## Webdriver installation

Since Selenium 4.6, **Selenium Manager** is bundled with the `selenium` package and downloads the matching
`chromedriver` / `geckodriver` (and Chrome for Testing when no browser is installed) on first use. No
`webdriver-manager`, no manual downloads and no `Service(executable_path=...)` are needed:

```python
from selenium import webdriver
driver = webdriver.Chrome()   # or webdriver.Firefox()
```

If you prefer system packages, on Debian/Ubuntu: `sudo apt install chromium chromium-driver`.

## Scripts

- `auto_installation_{chrome,chromium,firefox}.py`: local browsers with Selenium Manager.
- `webapp_firefox.py`: form login (credentials via `LOGIN_USERNAME` / `LOGIN_PASSWORD` env vars).
- `webapp_heartbeat.py`: periodic Chrome heartbeat.

Run any of them with `uv run <script>.py` (dependencies come from the script header; `pip install -r requirements.txt` also works).
