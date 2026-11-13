# Airflow 3.4 (CeleryExecutor) with docker compose

Adapted from the official [3.4.0 compose file](https://airflow.apache.org/docs/apache-airflow/3.4.0/docker-compose.yaml).
Services: `postgres` 16, `redis` 7.2, `airflow-apiserver`, `scheduler`, `dag-processor`, `worker`, `triggerer`, `airflow-init`, optional `flower` (profile).
Local development only.

## Run

Optional: copy `.env.example` to `.env` to override defaults (every variable has a default, so this is not required). On Linux set `AIRFLOW_UID` in `.env` to your user id (`id -u`) so files in `dags/` and `logs/` are not root-owned.

```bash
docker compose up airflow-init   # one-off DB migration + admin user
docker compose up -d
docker compose --profile flower up -d flower   # optional
docker compose down              # add -v to delete the metadata DB
```

- UI / API: http://localhost:8080 (user `airflow`, password `airflow`)
- Flower: http://localhost:5555 (profile `flower`)
- Put DAGs in `dags/` (see `dags/hello_airflow.py`, which uses the Airflow 3 `airflow.sdk`), plugins in `plugins/`; logs go to `logs/` (git-ignored).
- Run the CLI: `docker compose run --rm airflow-cli airflow dags list` (profile `debug`: add `--profile debug`).

## Environment (`.env`)

| Variable | Default |
|---|---|
| `AIRFLOW_IMAGE_NAME` | `apache/airflow:3.4.0` |
| `AIRFLOW_UID` | `50000` |
| `AIRFLOW_PORT` / `FLOWER_PORT` | `8080` / `5555` |
| `AIRFLOW_LOAD_EXAMPLES` | `false` |
| `FERNET_KEY` | empty (set your own) |
| `AIRFLOW__API_AUTH__JWT_SECRET` | `airflow_jwt_secret` (dev only) |
| `_AIRFLOW_WWW_USER_USERNAME` / `_PASSWORD` | `airflow` / `airflow` |

Needs ~4 GB RAM, 2 CPUs for Docker.
