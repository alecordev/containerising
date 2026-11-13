# DuckDB sandbox: the `duckdb` CLI plus the Python package (with pandas and pyarrow) on a slim Python image.
ARG PYTHON_VERSION=3.14
ARG DUCKDB_VERSION=2.0.0

FROM python:${PYTHON_VERSION}-slim-trixie AS cli
ARG DUCKDB_VERSION
ARG TARGETARCH
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL "https://github.com/duckdb/duckdb/releases/download/v${DUCKDB_VERSION}/duckdb-cli-linux-${TARGETARCH}.tar.gz" \
    | tar -xz -C /usr/local/bin duckdb \
    && chmod 0755 /usr/local/bin/duckdb

FROM python:${PYTHON_VERSION}-slim-trixie
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/duck

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY --from=cli /usr/local/bin/duckdb /usr/local/bin/duckdb

# /work/data is the volume mount point; create it owned by the runtime user so the named volume inherits that.
RUN useradd --create-home --uid 1000 duck \
    && mkdir -p /work/data /work/examples \
    && chown -R duck:duck /work
USER duck
WORKDIR /work

COPY --chown=duck:duck examples/ /work/examples/

CMD ["duckdb"]
