# Simple Selenium (Chrome)

Headless Chromium (Debian package) + chromedriver in a Python image, driven with Selenium 4.

```bash
docker compose up --build        # screenshot lands in ./output/screenshot.png
TARGET_URL=https://example.com docker compose up --build
```

`all_in_one.py` runs Chrome directly on your machine using Selenium Manager (no manual driver download).
