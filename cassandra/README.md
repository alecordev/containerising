# Apache Cassandra

`cassandra:5.0.9` as a single node with a small JVM heap for laptops. Compare with [`../scylladb`](../scylladb) (Cassandra-compatible).

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait     # first start takes ~1-2 minutes
docker compose down             # add -v to delete data
```

## Access

| What | Where |
|---|---|
| CQL native protocol | `localhost:9042` |
| Auth | none (default `AllowAllAuthenticator`), local development only |

```bash
docker compose exec cassandra cqlsh
```

```sql
CREATE KEYSPACE demo WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
CREATE TABLE demo.users (id uuid PRIMARY KEY, name text);
INSERT INTO demo.users (id, name) VALUES (uuid(), 'alice');
SELECT * FROM demo.users;
```

Python (`uv run --with cassandra-driver python`): `Cluster(["localhost"]).connect()`.

## Environment variables

| Variable | Default |
|---|---|
| `CASSANDRA_VERSION` | `5.0.9` |
| `CASSANDRA_CLUSTER_NAME` | `dev-cluster` |
| `CASSANDRA_DC` / `CASSANDRA_RACK` | `dc1` / `rack1` |
| `CASSANDRA_MAX_HEAP_SIZE` / `CASSANDRA_HEAP_NEWSIZE` | `512M` / `128M` |
| `CASSANDRA_CQL_PORT` | `9042` |

## Notes

- Host port 9042 clashes with `scylladb/`; set `CASSANDRA_CQL_PORT`.
- Needs roughly 1.5 GB RAM including the JVM; raise the heap for real workloads.
- Data lives in the named volume `cassandra-data`.

## Resources

- https://cassandra.apache.org/doc/latest/
- https://hub.docker.com/_/cassandra

## Smoke test

`python scripts/smoke.py cassandra` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run cassandra/smoke.py`); it needs only the Python standard library.
