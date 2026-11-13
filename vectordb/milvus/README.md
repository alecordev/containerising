# Milvus (standalone)

[Milvus](https://milvus.io/): scalable vector database. This template is the **standalone** deployment: Milvus + etcd (metadata) + MinIO (object storage), adapted from the official compose file. Object storage uses `milvusdb/minio`, the MinIO build published by the Milvus project.

**Heavy**: plan for roughly 2-4 GB of RAM and a slow first start (up to ~2 minutes). For something lighter use [qdrant](../qdrant) or [chroma](../chroma).

## Run

```bash
cd vectordb/milvus
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete all data volumes
```

A one-shot `milvus-volume-init` container fixes ownership of the data volume, then exits (it shows as `exited (0)`; that is expected).

## Ports and URLs

| What | URL | Env override |
|---|---|---|
| gRPC + REST v2 | localhost:19530 | `MILVUS_PORT` |
| Health / metrics | http://localhost:9091/healthz | `MILVUS_METRICS_PORT` |
| Object store console | http://localhost:9001 (`minioadmin` / `minioadmin`) | `MILVUS_MINIO_CONSOLE_PORT` |

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `MILVUS_VERSION` | `v3.0.6` | Image tag |
| `ETCD_VERSION` | `v3.5.25` | |
| `MINIO_VERSION` | `RELEASE.2024-12-18T13-15-44Z` | `milvusdb/minio` tag |
| `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` | `minioadmin` | Dev-only |

Authentication is off by default (Milvus default user `root`, password `Milvus` applies only once auth is enabled).

## Try it (REST v2)

```python
import json, urllib.request

BASE = "http://localhost:19530/v2/vectordb"

def post(path, body):
    req = urllib.request.Request(f"{BASE}/{path}", method="POST", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

post("collections/create", {"collectionName": "demo", "dimension": 4})
post("entities/insert", {"collectionName": "demo", "data": [{"id": 1, "vector": [0.1, 0.2, 0.3, 0.4]}]})
print(post("entities/search", {"collectionName": "demo", "data": [[0.1, 0.2, 0.3, 0.4]], "annsField": "vector", "limit": 3}))
post("collections/drop", {"collectionName": "demo"})
```

Python (`uv run --with pymilvus python`): `MilvusClient(uri="http://localhost:19530")`.

## Resources

- https://milvus.io/docs/install_standalone-docker-compose.md
- https://milvus.io/api-reference/restful/v2.6.x/About.md

## Smoke test

`python scripts/smoke.py vectordb/milvus` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run vectordb/milvus/smoke.py`); it needs only the Python standard library.
