# ScyllaDB

`scylladb/scylla:2026.3`, single node, dev-sized (`--smp 1 --memory 750M --overprovisioned 1`).

```bash
docker compose up -d
docker compose exec scylla cqlsh        # CQL shell (node needs ~1 minute to become ready)
uv run src/conn.py                      # connection check (installs scylla-driver on first run)
```

| Variable | Default |
|---|---|
| `SCYLLA_CQL_PORT` | `9042` |
| `SCYLLA_SMP` | `1` |
| `SCYLLA_MEMORY` | `750M` |

Scripts in `src/` read `SCYLLA_HOSTS` (comma separated, default `localhost`) and `SCYLLA_PORT` (default `9042`).
Data lives in the named volume `scylla-data`. The legacy Thrift port (9160) is no longer published.

## Reference

- https://python-driver.docs.scylladb.com/stable/getting-started.html
