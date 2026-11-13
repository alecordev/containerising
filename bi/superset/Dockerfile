# Apache Superset + the PostgreSQL driver the official image lacks (it ships Redis support only).
# The image's own virtualenv is /app/.venv and has no pip: use the bundled `uv`.
ARG SUPERSET_VERSION=6.1.0
FROM apache/superset:${SUPERSET_VERSION}

USER root
RUN uv pip install --no-cache --python /app/.venv/bin/python psycopg2-binary
USER superset
