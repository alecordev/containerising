# Apache Superset

[Apache Superset](https://superset.apache.org) `6.1.0` (SQL Lab, charts, dashboards) with a PostgreSQL 18 metadata database and Redis for caching.

| Service | Image | Purpose |
|---|---|---|
| `superset` | `local/superset:6.1.0` (built from `apache/superset:6.1.0`) | web app (gunicorn, port 8088) |
| `superset-init` | same | one-shot: `superset db upgrade`, create the admin user, `superset init`, then exits 0 |
| `postgres` | `postgres:18-alpine` | metadata (users, charts, dashboards) |
| `redis` | `redis:8.8-alpine` | query/metadata/filter-state caches |

The official image has no PostgreSQL driver, so the small `Dockerfile` adds `psycopg2-binary` with the `uv` that ships in the image. Configuration lives in `superset_config.py`, mounted at `/app/pythonpath/superset_config.py`.

## Run

```bash
docker compose up -d --build --wait     # copy .env.example to .env first to override defaults (optional)
docker compose down                     # add -v to delete dashboards, users and cache
```

The first start takes a few minutes (image build, database migrations, role initialisation).

- UI: http://localhost:8088, login `admin` / `admin`
- Health: http://localhost:8088/health (returns `OK`)

## Connect your data

Superset connects from inside the container, so `localhost` means the container itself. To reach a database from another template, use `host.docker.internal` and the published port (on Linux add `extra_hosts: ["host.docker.internal:host-gateway"]`), or join the other stack's network. In *Settings > Database Connections* use SQLAlchemy URIs such as `postgresql+psycopg2://postgres:postgres@host.docker.internal:5432/postgres`.

Only PostgreSQL and Redis drivers are installed. For other engines extend the `Dockerfile`, for example
`RUN uv pip install --no-cache --python /app/.venv/bin/python clickhouse-connect` (see the [driver list](https://superset.apache.org/docs/configuration/databases)).

## Environment

| Variable | Default |
|---|---|
| `SUPERSET_VERSION` | `6.1.0` |
| `SUPERSET_PORT` | `8088` |
| `SUPERSET_SECRET_KEY` | dev-only value, **change it** (`python -c "import secrets; print(secrets.token_urlsafe(42))"`) |
| `SUPERSET_ADMIN_USER` / `SUPERSET_ADMIN_PASSWORD` / `SUPERSET_ADMIN_EMAIL` | `admin` / `admin` / `admin@superset.local` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `superset` |

## Notes

- Needs ~2 GB RAM. Superset refuses to start with its built-in placeholder `SECRET_KEY`, which is why a dev default is set in the compose file; use your own beyond localhost.
- `TALISMAN_ENABLED = False` in `superset_config.py` because there is no TLS in front of this dev stack.
- Example dashboards are not loaded. To add them: `docker compose exec superset superset load_examples`.
- Port 8088 does not clash with the other templates (Metabase, Open WebUI and Langfuse use 3000).

## Verify

`python ../../scripts/smoke.py bi/superset` brings the stack up, checks `/health`, logs in through the REST API as the admin user, checks the metadata DB, and tears everything down. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run bi/superset/smoke.py`).

## Resources

- https://superset.apache.org/docs/installation/docker-compose · https://superset.apache.org/docs/configuration/configuring-superset
