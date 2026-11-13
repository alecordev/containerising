# syntax=docker/dockerfile:1
# Install dependencies into an isolated prefix in a builder stage, copy the prefix to the runtime stage.
FROM python:3.14-slim-trixie AS base

FROM base AS builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install --prefix=/install -r /requirements.txt

FROM base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 1000 app
COPY --from=builder /install /usr/local
COPY --chown=app:app src /app
WORKDIR /app
USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"

CMD ["gunicorn", "-w", "2", "--bind", "0.0.0.0:8000", "main:app"]
