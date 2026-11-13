# MLflow tracking server

MLflow `3.18.0` with a PostgreSQL 18 metadata store. Artifacts are kept in a Docker volume and proxied through the server (`--serve-artifacts`), so clients only need HTTP access. The small `Dockerfile` adds `psycopg2-binary` and `boto3` to the official image.

## Run

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --build --wait
docker compose down      # add -v to delete experiments and artifacts
```

UI and API: http://localhost:5000

## Log a run

```bash
uv run example.py        # dependencies come from the script header (generated from requirements.txt)
```

Or `uv sync` then `uv run python example.py` (project environment from `pyproject.toml`); plain `pip install -r requirements.txt` still works.

Or from any project, set `MLFLOW_TRACKING_URI=http://localhost:5000` (bash: `export ...`, PowerShell: `$env:MLFLOW_TRACKING_URI = "..."`) or call `mlflow.set_tracking_uri(...)`.

## Environment

| Variable | Default |
|---|---|
| `MLFLOW_VERSION` | `v3.18.0` (image tag) |
| `MLFLOW_PORT` | `5000` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `mlflow` |

## Notes

- To use S3-compatible storage instead, change `--artifacts-destination` to `s3://bucket` and set `MLFLOW_S3_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (boto3 is installed). Pair it with an S3-compatible service.
- MLflow 3 validates the `Host` header. If you reach the server by another hostname, add `--allowed-hosts` to the command.
- The pinned `mlflow-skinny` in `requirements.txt` matches the server version.

## Verify

`python ../scripts/smoke.py mlflow` brings the stack up, runs `smoke.py` (creates an experiment and run through the REST API, logs a metric, uploads an artifact through the proxy) and tears it down. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run mlflow/smoke.py`).

## Resources

- https://mlflow.org/docs/latest/self-hosting/
