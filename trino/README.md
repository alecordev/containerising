# Trino

Single-node Trino `484` (coordinator and worker in one container) with two catalogs:

| Catalog | Connector | Use |
|---|---|---|
| `tpch` | TPC-H generator | benchmark data on demand, schemas `tiny`, `sf1`, `sf10`... |
| `memory` | in-memory tables | scratch tables, lost on restart |

## Run

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down
```

- Web UI: http://localhost:8080 (any username, no password)

## Query

```bash
docker compose exec trino trino                 # interactive shell
docker compose exec trino trino --execute "SELECT name FROM tpch.tiny.nation ORDER BY 1 LIMIT 5"
docker compose exec trino trino --execute "SHOW CATALOGS"
```

From Python (`uv run --with trino python`):
`trino.dbapi.connect(host="localhost", port=8080, user="me", catalog="tpch", schema="tiny")`.

## Add a catalog

Create `catalog/<name>.properties` and `docker compose restart trino`. Examples:

```properties
# catalog/postgres.properties  (see ../postgresql)
connector.name=postgresql
connection-url=jdbc:postgresql://host.docker.internal:5432/postgres
connection-user=postgres
connection-password=postgres
```

The same pattern works for `mysql`, `mongodb`, `clickhouse`, `kafka`, `iceberg` and others (for Iceberg you also need a metastore and object storage).

## Environment

| Variable | Default |
|---|---|
| `TRINO_VERSION` | `484` |
| `TRINO_PORT` | `8080` |

## Notes

- The image ships its default single-node `config.properties` and `jvm.config`; only `/etc/trino/catalog` is mounted. Plan on ~2-4 GB RAM.
- `memory` tables disappear on restart; there is no persistent storage in this template.

## Verify

`python ../scripts/smoke.py trino` brings the stack up, runs `smoke.py` (queries `tpch.tiny.nation` and round-trips a table through the `memory` catalog) and tears it down. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run trino/smoke.py`).

## Resources

- https://trino.io/docs/current/ · https://trino.io/docs/current/installation/containers.html
