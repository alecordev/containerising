# Prefect 3 server

Prefect 3 API + UI (`prefecthq/prefect:3.9.2-python3.13`) on PostgreSQL 18. This replaces the discontinued Prefect 1 stack (Hasura/Apollo/towel).

## Run

Optional: copy `.env.example` to `.env` to override defaults (every variable has a default, so this is not required).

```bash
docker compose up -d
docker compose down    # add -v to delete the database
```

- UI: http://localhost:4200  — API docs: http://localhost:4200/docs
- Postgres is internal to the compose network (not published).

## Run the example flow

```bash
uv run prefect config set PREFECT_API_URL=http://localhost:4200/api   # works in every shell
uv run example/hello.py          # one run, visible in the UI
uv run example/hello.py serve    # deployment on a 1-minute cron
```

## Optional worker (profile `worker`)

```bash
docker compose run --rm server prefect work-pool create default --type process
docker compose --profile worker up -d worker
```

## Environment

| Variable | Default |
|---|---|
| `PREFECT_VERSION` | `3.9.2-python3.13` |
| `PREFECT_PORT` | `4200` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `prefect` |

Resources: https://docs.prefect.io/v3/get-started
