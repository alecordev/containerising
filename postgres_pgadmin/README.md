# PostgreSQL & PgAdmin

Images: `postgres:18.6-alpine`, `dpage/pgadmin4:9.19`.

## Quick Start

```bash
docker compose up -d
```

## Environment variables

| Variable | Default |
|---|---|
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | `postgres` |
| `PG_PORT` | `5432` |
| `PGADMIN_PORT` | `5050` |
| `PGADMIN_DEFAULT_EMAIL` | `pgadmin@pgadmin.org` |
| `PGADMIN_DEFAULT_PASSWORD` | `admin` |

## Access to postgres

- `localhost:5432`, user/password: `postgres` / `postgres` (defaults)

## Access to pgAdmin

- URL: http://localhost:5050
- Login: `pgadmin@pgadmin.org` / `admin` (defaults)

### Add a new server in pgAdmin

- Host name/address: `postgres`
- Port: `5432`
- Username / password: `POSTGRES_USER` / `POSTGRES_PASSWORD`

## Notes

- Data is stored in the named volumes `pgdata` (mounted at `/var/lib/postgresql`, the PostgreSQL 18+ layout) and `pgadmin` (`/var/lib/pgadmin`).
- Reset everything: `docker compose down -v`.
