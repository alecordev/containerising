# Metabase

[Metabase](https://www.metabase.com) open-source BI `v0.65.4` with a PostgreSQL 18 application database.

## Run

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down      # add -v to delete dashboards and settings
```

UI: http://localhost:3000. The first start takes about a minute (migrations); the setup wizard asks for an admin user. A **Sample Database** is included.

## Connect your data

Metabase connects from inside the container, so `localhost` is the container itself. Options:

- A database from another template on the same machine: host `host.docker.internal`, the published port, e.g. Postgres on `host.docker.internal:5432` (see [`../../postgresql`](../../postgresql)).
- Join the other stack's network: add `networks: {other: {external: true, name: <network>}}` to the `metabase` service and use the service name as host.

## Environment

| Variable | Default |
|---|---|
| `METABASE_VERSION` | `v0.65.4` |
| `METABASE_PORT` | `3000` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `metabase` |
| `TZ` | `UTC` |

## Notes

- Needs ~1.5 GB RAM. Change the database password and set `MB_ENCRYPTION_SECRET_KEY` before keeping real connection secrets in it.
- Metabase and Superset ([`../superset`](../superset)) both default to different ports (3000 / 8088), but 3000 also collides with Open WebUI and Langfuse; override with `METABASE_PORT`.

## Verify

`python ../../scripts/smoke.py bi/metabase` brings the stack up, runs `smoke.py` (runs the first-time setup through the API, logs in and lists the Sample Database) and tears it down. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run bi/metabase/smoke.py`).

## Resources

- https://www.metabase.com/docs/latest/installation-and-operation/running-metabase-on-docker
