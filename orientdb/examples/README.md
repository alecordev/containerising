# OrientDB examples

`pyorient` (binary protocol client) is unmaintained and does not work with OrientDB 3.x, so these examples use
OrientDB's HTTP/REST API (port 2480) through `requests`.

```bash
uv run simple.py     # connect and check whether a database exists
uv run example.py    # create a graph database, vertices and edges, then query them
```

Settings (env vars): `ORIENTDB_URL` (default `http://localhost:2480`), `ORIENTDB_ROOT_PASSWORD` (default `root`).
Studio UI: http://localhost:2480

## Reference

- https://orientdb.org/docs/3.2.x/misc/OrientDB-REST.html
- https://orientdb.org/docs/3.2.x/sql/SQL-Syntax.html
