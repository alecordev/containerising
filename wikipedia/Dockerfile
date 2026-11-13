# syntax=docker/dockerfile:1
# Two images from one file:
#   target "downloader": Python tool (prep/wiki.py) that resolves, downloads and verifies ZIM snapshots into /data
#   target "server":     kiwix-serve, which serves every /data/*.zim with browsing + full-text search
ARG PYTHON_VERSION=3.14
ARG KIWIX_VERSION=3.8.2

FROM python:${PYTHON_VERSION}-slim-trixie AS downloader
ENV PYTHONUNBUFFERED=1     PYTHONDONTWRITEBYTECODE=1     WIKI_DATA_DIR=/data
RUN useradd --create-home --uid 10001 app     && mkdir /data     && chown app:app /data
WORKDIR /app
COPY prep/wiki.py ./wiki.py
USER app
VOLUME /data
ENTRYPOINT ["python", "/app/wiki.py"]
CMD ["download"]

FROM ghcr.io/kiwix/kiwix-serve:${KIWIX_VERSION} AS server
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5     CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
