# DuckDB sandbox

An in-process analytical database, packaged for quick experiments: the `duckdb` CLI **2.0.0** and the Python package with pandas and pyarrow, on `python:3.14-slim-trixie`, running as a non-root user.

DuckDB is a library, not a server, so this template starts an **idle container** (`sleep infinity`) that you drive with `docker compose exec`.

## Run

```bash
docker compose up -d --build --wait

# interactive SQL shell (database in memory)
docker compose exec duckdb duckdb

# persistent database file in the duckdb-data volume
docker compose exec duckdb duckdb /work/data/my.duckdb

# run the examples
docker compose exec duckdb duckdb -f /work/examples/example.sql
docker compose exec duckdb python /work/examples/example.py

docker compose down      # add -v to delete the data volume
```

A throwaway container works too: `docker compose run --rm duckdb duckdb`.

## Files

- `/work/data` is the `duckdb-data` named volume (databases and exports). Copy a file out to the host with
  `docker compose cp duckdb:/work/data/trades.parquet .` (works the same on every OS).
- `/work/examples` is `./examples` mounted read-only: edit and re-run without rebuilding.
- To query host files, add a bind mount under `volumes:` in `docker-compose.yml`, for example
  `- ./mydata:/work/mydata:ro`, then `docker compose up -d` again.

## Useful snippets

```sql
SELECT * FROM 'file.parquet';                       -- query a file directly
SELECT * FROM read_csv('https://example.com/x.csv'); -- remote file (httpfs auto-loads)
INSTALL postgres; LOAD postgres;                     -- attach a running Postgres, see ../postgresql
ATTACH 'host=host.docker.internal user=postgres password=postgres dbname=postgres' AS pg (TYPE postgres);
```

## Environment

| Variable | Default |
|---|---|
| `DUCKDB_VERSION` | `2.0.0` (CLI release and image tag) |
| `PYTHON_VERSION` | `3.14` |

If you change `DUCKDB_VERSION`, update `requirements.txt` too.

## Verify

`python ../scripts/smoke.py duckdb` builds, starts, runs the CLI and both examples (see `smoke.py`), and tears down. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run duckdb/smoke.py`).

## Resources

- https://duckdb.org/docs/
