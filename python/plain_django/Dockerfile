# syntax=docker/dockerfile:1
FROM python:3.14-slim-trixie AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt


FROM python:3.14-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN useradd --create-home --uid 1000 app \
    && mkdir /data && chown app:app /data

COPY --from=builder /opt/venv /opt/venv
WORKDIR /app
COPY --chown=app:app example/ /app/

# Collect admin static files for WhiteNoise (build-time key is irrelevant)
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput \
    && chown -R app:app /app/staticfiles

USER app
ENV DJANGO_DB_PATH=/data/db.sqlite3
VOLUME /data
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen(urllib.request.Request('http://localhost:8000/admin/login/', headers={'Host': 'localhost'}))"

CMD ["sh", "-c", "python manage.py migrate --noinput && exec gunicorn example.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3}"]
