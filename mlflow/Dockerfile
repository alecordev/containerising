# MLflow tracking server + the extras the official image lacks (PostgreSQL driver, S3 client).
ARG MLFLOW_VERSION=v3.18.0
FROM ghcr.io/mlflow/mlflow:${MLFLOW_VERSION}

RUN pip install --no-cache-dir psycopg2-binary boto3

EXPOSE 5000
