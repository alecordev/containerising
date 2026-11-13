# PostgreSQL

PostgreSQL 18 (`postgres:18.6-alpine`) with an init schema (`schema.sql`) and a
custom config (`postgres.conf`).

## Run

```bash
docker compose up -d
psql -h localhost -p 5432 -U postgres -d blog     # password: postgres
```

Useful `psql` commands: `\l` list databases, `\c blog` connect, `\dt` list tables.

## Configuration (env vars, optional `.env`, see `.env.example`)

| Variable | Default |
|---|---|
| `PG_PORT` | `5432` |
| `POSTGRES_DB` | `blog` |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | `postgres` |

## Notes

- `schema.sql` only runs on the **first** start of an empty volume. To re-run it: `docker compose down -v`.
- Data lives in the named volume `pgdata`, mounted at `/var/lib/postgresql` (required layout for PostgreSQL 18+).
- `postgres.conf` is a small override file, loaded through `command: postgres -c config_file=...`.
