# OrientDB

Two-node OrientDB 3.2 distributed setup (`orientdb:3.2.58`, `dserver.sh`): `odb2` joins `odb1` once it is healthy.

```bash
docker compose up -d --wait
docker compose down        # add -v to delete both databases
```

- Studio UI: http://localhost:2480 (login `root` / `root`)
- Binary protocol: `localhost:2424`
- REST API: http://localhost:2480 (e.g. `GET /listDatabases`)

Only `odb1` publishes ports; `odb2` is reachable from `odb1` inside the compose network.

| Variable | Default | Description |
|---|---|---|
| `ORIENTDB_ROOT_PASSWORD` | `root` | root password (applies on first start of an empty volume) |
| `ORIENTDB_STUDIO_PORT` | `2480` | host port for Studio / REST |
| `ORIENTDB_BINARY_PORT` | `2424` | host port for the binary protocol |

Each node keeps its databases in a named volume (`odb1-databases`, `odb2-databases`).

## Python examples

`pyorient` does not support OrientDB 3.x, so `examples/` uses the REST API with `requests`; see
[examples/README.md](examples/README.md).

## Checks

`python scripts/smoke.py orientdb` starts the stack, waits for healthy and runs `smoke.py` (REST `/listDatabases`). With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run orientdb/smoke.py`).

## Resources

- https://orientdb.org/docs/3.2.x/
- https://orientdb.org/docs/3.2.x/misc/OrientDB-REST.html
