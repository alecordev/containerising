# Qdrant

[Qdrant](https://qdrant.tech/): high-performance vector database with payload filtering, a REST + gRPC API and a built-in web UI.

## Run

```bash
cd vectordb/qdrant
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete the storage volume
```

## Ports and URLs

| What | URL | Env override |
|---|---|---|
| REST API | http://localhost:6333 | `QDRANT_HTTP_PORT` |
| Web UI | http://localhost:6333/dashboard | |
| gRPC | localhost:6334 | `QDRANT_GRPC_PORT` |

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `QDRANT_VERSION` | `v1.20.0` | Image tag |
| `QDRANT_API_KEY` | *(empty)* | Empty = no auth. When set, send `api-key: <value>` |

## Try it

```python
import json, urllib.request

def call(method, url, body=None):
    req = urllib.request.Request(url, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

BASE = "http://localhost:6333"   # add an "api-key" header if QDRANT_API_KEY is set
call("PUT", f"{BASE}/collections/demo", {"vectors": {"size": 4, "distance": "Cosine"}})
call("PUT", f"{BASE}/collections/demo/points?wait=true",
     {"points": [{"id": 1, "vector": [0.1, 0.2, 0.3, 0.4], "payload": {"name": "a"}}]})
print(call("POST", f"{BASE}/collections/demo/points/search",
           {"vector": [0.1, 0.2, 0.3, 0.4], "limit": 3, "with_payload": True}))
```

Python (`uv run --with qdrant-client python`): `QdrantClient(url="http://localhost:6333")` (or `QdrantClient(":memory:")` with no server).

## Notes

- The image ships only `bash` (no curl/wget), so the healthcheck probes `/readyz` through bash's `/dev/tcp`.

## Resources

- https://qdrant.tech/documentation/
- https://qdrant.tech/documentation/guides/installation/#docker

## Smoke test

`python scripts/smoke.py vectordb/qdrant` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run vectordb/qdrant/smoke.py`); it needs only the Python standard library.
