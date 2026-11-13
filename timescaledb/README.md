# TimescaleDB

PostgreSQL 18 with the TimescaleDB time-series extension: `timescale/timescaledb:2.32.0-pg18` (Community edition under the Timescale License, includes compression and continuous aggregates; use `TIMESCALE_VERSION=2.32.0-pg18-oss` for the Apache-2-only build with fewer features).

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down      # add -v to delete data
```

## Access

| What | Value |
|---|---|
| Host / port | `localhost:5432` |
| Login | `postgres` / `postgres`, database `postgres` |

```bash
docker compose exec timescaledb psql -U postgres
psql postgresql://postgres:postgres@localhost:5432/postgres
```

On first start `initdb/01-hypertable.sql` creates a `conditions` hypertable with one row:

```sql
SELECT time_bucket('1 hour', time) AS bucket, device, avg(temperature)
FROM conditions GROUP BY bucket, device ORDER BY bucket;
```

## Environment variables

| Variable | Default |
|---|---|
| `TIMESCALE_VERSION` | `2.32.0-pg18` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `postgres` / `postgres` / `postgres` |
| `PG_PORT` | `5432` |

Credentials only apply on the first start of an empty volume. Data lives in the named volume `timescale-data` (mounted at `/var/lib/postgresql`, as required by PostgreSQL 18 images).

## Notes

- Host port 5432 clashes with the other Postgres templates; override `PG_PORT`.
- `docker compose down -v` resets the database.

## Resources

- https://docs.timescale.com/
- https://hub.docker.com/r/timescale/timescaledb

## Smoke test

`python scripts/smoke.py timescaledb` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run timescaledb/smoke.py`); it needs only the Python standard library.
