# Selenium

Selenium 4.52.0 images and Python examples (Selenium Python bindings `selenium==4.52.0`).

## Selenium Grid (hub + nodes)

Optional: copy `.env.example` to `.env` to override defaults (every variable has a default, so this is not required).

```bash
docker compose up -d                       # hub + Chrome + Firefox
docker compose --profile edge up -d        # also Edge (linux/amd64 only; no arm64 image exists)
docker compose up -d --scale chrome=3      # more parallel sessions
```

- Grid UI / WebDriver endpoint: http://localhost:4444
- Each node serves noVNC on port 7900 inside the container; host ports are assigned dynamically so nodes
  can be scaled: `docker compose port chrome 7900` (VNC password: `SE_VNC_PASSWORD`, default `secret`).

## Standalone (one container: browser + server)

```bash
docker compose -f docker-compose.standalone.yml up -d              # Chrome
BROWSER=firefox docker compose -f docker-compose.standalone.yml up -d
```

WebDriver: http://localhost:4444, noVNC: http://localhost:7900 (password `secret`).
Or without compose: `docker run -d -p 4444:4444 -p 7900:7900 --shm-size=2g selenium/standalone-firefox:4.52.0`.

Python (`uv run --with selenium python`):

```python
from selenium import webdriver
driver = webdriver.Remote(command_executor="http://localhost:4444", options=webdriver.FirefoxOptions())
```

## Layout

- `src/examples`: Remote/Grid examples (read `GRID_URL`, default `http://localhost:4444`). Run with uv, e.g. `uv run src/examples/simple.py` (dependencies come from the script header; `requirements.txt` stays for pip).
- `src/simple-chrome`, `src/simple-firefox`: Python image with a headless browser baked in (`docker compose up --build`).
- `src/selenium_stand_alone.py`, `utils/`: scripts that start a standalone container, wait for `/status`, use it and clean up.
- `summary/`: local-browser scripts using Selenium Manager.

## Resources

- https://github.com/SeleniumHQ/docker-selenium
