# PostgreSQL with the pgvector extension

PostgreSQL 18.6 + [pgvector](https://github.com/pgvector/pgvector) **v0.8.7**, built from source in a
multi-stage `Dockerfile` (the compiler toolchain is not in the final image).

## Run

```bash
docker compose up -d --build
psql -h localhost -U postgres -c "SELECT '[1,2,3]'::vector <-> '[3,2,1]';"   # password: postgres
```

## Configuration

| Variable | Default |
|---|---|
| `PG_PORT` | `5432` |
| `POSTGRES_DB` | `postgres` |
| `POSTGRES_USER` | `postgres` |
| `POSTGRES_PASSWORD` | `postgres` |

Build args (in `docker-compose.yml`): `POSTGRES_VERSION`, `PGVECTOR_VERSION` (a git tag of pgvector).

## Notes

- `vector_extension.sql` (mounted as `0-...`) runs first and creates the extension in `POSTGRES_DB`; put your own SQL in `init.sql`. Init scripts only run on the first start of an empty volume (`docker compose down -v` to reset).
- Data lives in the named volume `pgdata` (PostgreSQL 18+ layout: mounted at `/var/lib/postgresql`).
- No-build alternative: use the official image `pgvector/pgvector:0.8.7-pg18-trixie` instead of the `build:` section.
