# syntax=docker/dockerfile:1
# Compile C extensions with gcc in the builder; ship only wheels to the slim runtime image.

FROM python:3.14-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# --no-binary forces a real compile so the gcc stage is actually exercised
RUN pip wheel --wheel-dir /app/wheels --no-binary psutil -r requirements.txt


FROM python:3.14-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN --mount=type=bind,from=builder,source=/app/wheels,target=/wheels \
    --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --no-index --find-links=/wheels -r /tmp/requirements.txt

RUN useradd --create-home --uid 1000 app
USER app

CMD ["python", "-c", "import psutil, yaml; print('psutil', psutil.__version__, '| PyYAML', yaml.__version__)"]
