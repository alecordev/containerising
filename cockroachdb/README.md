# CockroachDB

Distributed, PostgreSQL-compatible SQL database: `cockroachdb/cockroach:v26.4.0`, run as a **single insecure node** for local development.

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down      # add -v to delete data
```

## Access

| What | Where |
|---|---|
| SQL (PostgreSQL wire protocol) | `localhost:26257` |
| Admin UI | http://localhost:8080 |
| Login | user `root`, **no password** (insecure mode), database `app` |

```bash
docker compose exec cockroach cockroach sql --insecure -d app
psql "postgresql://root@localhost:26257/app?sslmode=disable"      # any Postgres client works
```

Connection string: `postgresql://root@localhost:26257/app?sslmode=disable` (SQLAlchemy: `cockroachdb://root@localhost:26257/app?sslmode=disable`).

## Environment variables

| Variable | Default |
|---|---|
| `COCKROACH_VERSION` | `v26.4.0` |
| `COCKROACH_DATABASE` | `app` (created on first start) |
| `COCKROACH_SQL_PORT` / `COCKROACH_UI_PORT` | `26257` / `8080` |

## Notes

- **Insecure mode** (`--insecure`) disables TLS and authentication. Never expose it beyond localhost. For a secure cluster follow the [official guide](https://www.cockroachlabs.com/docs/stable/secure-a-cluster).
- **Licensing**: CockroachDB is under the CockroachDB Software License. Single-node clusters used for development/testing need no license key; multi-node self-hosted clusters need an Enterprise license (a free tier exists). See the [licensing FAQs](https://docs.cockroachlabs.com/docs/stable/licensing-faqs).
- Admin UI port 8080 clashes with `airflow/`, `spark/` and others; set `COCKROACH_UI_PORT`.

## Resources

- https://www.cockroachlabs.com/docs/stable/
- https://hub.docker.com/r/cockroachdb/cockroach

## Smoke test

`python scripts/smoke.py cockroachdb` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run cockroachdb/smoke.py`); it needs only the Python standard library.
