# One image, three roles (webserver, daemon, user-code gRPC server), chosen by `command:` in compose.
FROM python:3.13-slim-trixie AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt


FROM python:3.13-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DAGSTER_HOME=/opt/dagster/dagster_home

RUN useradd --create-home --uid 1000 dagster \
    && mkdir -p "$DAGSTER_HOME/storage" /opt/dagster/app \
    && chown -R dagster:dagster /opt/dagster

COPY --from=builder /opt/venv /opt/venv
COPY --chown=dagster:dagster dagster.yaml workspace.yaml "$DAGSTER_HOME/"
COPY --chown=dagster:dagster pipeline /opt/dagster/app/pipeline

WORKDIR /opt/dagster/app
USER dagster

EXPOSE 3000 4000

# Default role: the user-code gRPC server that hosts `pipeline.definitions`.
CMD ["dagster", "api", "grpc", "--host", "0.0.0.0", "--port", "4000", "--module-name", "pipeline.definitions"]
