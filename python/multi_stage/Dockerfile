# syntax=docker/dockerfile:1
# Multi-stage "wheelhouse" pattern: build wheels in a fat image, install them in a slim one.

FROM python:3.14-slim-trixie AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY requirements.txt .
RUN pip wheel --wheel-dir /wheels -r requirements.txt


FROM python:3.14-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --create-home --uid 1000 jovyan
WORKDIR /notebooks

RUN --mount=type=bind,from=builder,source=/wheels,target=/wheels \
    --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --no-index --find-links=/wheels -r /tmp/requirements.txt \
    && chown jovyan:jovyan /notebooks

USER jovyan
EXPOSE 8888

# Set JUPYTER_TOKEN at runtime to protect the server (empty token = no auth, local dev only).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8888/api').status == 200 else 1)"

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--notebook-dir=/notebooks"]
