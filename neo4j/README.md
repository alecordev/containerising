# Neo4j

`neo4j:2026.10-community` with the APOC plugin enabled.

```bash
docker compose up -d
```

- Browser: http://localhost:7474
- Bolt: `bolt://localhost:7687`, login `neo4j` / `password`

| Variable | Default |
|---|---|
| `NEO4J_PASSWORD` | `password` (must be at least 8 characters) |
| `NEO4J_HTTP_PORT` / `NEO4J_BOLT_PORT` | `7474` / `7687` |
| `NEO4J_HEAP_MAX` | `1G` |

Data, logs and plugins live in named volumes; `./.docker/import` is mounted at `/import` for `LOAD CSV`.
The password only takes effect on the **first** start of an empty volume (`docker compose down -v` to reset).

## Python examples

```bash
uv run examples/neo4j_example.py      # official driver (dependencies come from the script header)
uv run examples/neomodel_example.py   # OGM
```

They read `NEO4J_URI` (default `bolt://localhost:7687`), `NEO4J_USER` (`neo4j`) and `NEO4J_PASSWORD` (`password`).
