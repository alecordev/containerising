# ClickHouse

Column-oriented OLAP database: `clickhouse/clickhouse-server:26.8-alpine` (a long-term-support release line; set `CLICKHOUSE_VERSION` to change).

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down      # add -v to delete data
```

## Access

| What | Where |
|---|---|
| HTTP interface / API | http://localhost:8123 (`/ping` health) |
| Play UI (built-in web SQL editor) | http://localhost:8123/play |
| Native protocol | `localhost:9000` |
| Login | `clickhouse` / `clickhouse` |

```bash
docker compose exec clickhouse clickhouse-client --user clickhouse --password clickhouse
```

```sql
CREATE TABLE events (ts DateTime, user String, n UInt32) ENGINE = MergeTree ORDER BY ts;
INSERT INTO events VALUES (now(), 'alice', 1);
SELECT user, sum(n) FROM events GROUP BY user;
```

HTTP example: `curl "http://localhost:8123/?user=clickhouse&password=clickhouse" --data-binary "SELECT version()"`.

## Environment variables

| Variable | Default |
|---|---|
| `CLICKHOUSE_VERSION` | `26.8-alpine` |
| `CLICKHOUSE_USER` / `CLICKHOUSE_PASSWORD` | `clickhouse` / `clickhouse` |
| `CLICKHOUSE_DB` | `default` |
| `CLICKHOUSE_HTTP_PORT` / `CLICKHOUSE_NATIVE_PORT` | `8123` / `9000` |

User, password and database are only applied on the first start of an empty volume. Data and logs live in named volumes.

## Notes

- Host port `9000` (native protocol) is commonly used by other tools (e.g. MinIO, Portainer); override with `CLICKHOUSE_NATIVE_PORT`.
- `nofile` ulimit is raised to 262144 as recommended by ClickHouse.

## Resources

- https://clickhouse.com/docs
- https://hub.docker.com/r/clickhouse/clickhouse-server

## Smoke test

`python scripts/smoke.py clickhouse` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run clickhouse/smoke.py`); it needs only the Python standard library.
