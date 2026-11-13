# syntax=docker/dockerfile:1
# Headless Firefox ESR (Debian) + geckodriver, resolved by Selenium Manager at build time.
FROM python:3.14-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    FIREFOX_BIN=/usr/bin/firefox-esr \
    SE_CACHE_PATH=/opt/selenium-cache

RUN apt-get update \
    && apt-get install -y --no-install-recommends firefox-esr fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Pre-download geckodriver into SE_CACHE_PATH so containers need no extra download at runtime.
RUN pip install -r requirements.txt \
    && python -c "from selenium.webdriver.common.selenium_manager import SeleniumManager; print(SeleniumManager().binary_paths(['--browser', 'firefox', '--browser-path', '/usr/bin/firefox-esr']))" \
    && chmod -R a+rwX /opt/selenium-cache

RUN useradd --create-home --uid 1000 app
WORKDIR /app
COPY --chown=app:app ./app /app
USER app

CMD ["python", "app.py"]
