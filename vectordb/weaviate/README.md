# Weaviate

[Weaviate](https://weaviate.io/): vector database with hybrid (BM25 + vector) search, multi-tenancy and optional vectorizer/generative modules. This template runs it **without a vectorizer** and with **anonymous access** (bring your own embeddings).

## Run

```bash
cd vectordb/weaviate
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete the data volume
```

## Ports and URLs

| What | URL | Env override |
|---|---|---|
| REST / GraphQL | http://localhost:8080 | `WEAVIATE_HTTP_PORT` |
| gRPC | localhost:50051 | `WEAVIATE_GRPC_PORT` |

Port 8080 collides with several other templates (Airflow, Spark, lamp); override it when running them together.

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `WEAVIATE_VERSION` | `1.40.5` | Image tag |
| `WEAVIATE_MODULES` | *(empty)* | e.g. `text2vec-openai,generative-openai`; also set `OPENAI_APIKEY` |
| `OPENAI_APIKEY` | *(empty)* | Only for OpenAI modules |

## Try it

```python
import json, urllib.request

def call(method, url, body=None):
    req = urllib.request.Request(url, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

BASE = "http://localhost:8080/v1"
call("POST", f"{BASE}/schema", {"class": "Doc", "vectorizer": "none", "properties": [{"name": "name", "dataType": ["text"]}]})
call("POST", f"{BASE}/objects", {"class": "Doc", "properties": {"name": "a"}, "vector": [0.1, 0.2, 0.3, 0.4]})
query = "{ Get { Doc(nearVector:{vector:[0.1,0.2,0.3,0.4]}, limit:3){ name } } }"
print(call("POST", f"{BASE}/graphql", {"query": query}))
```

Python (`uv run --with weaviate-client python`, v4): `weaviate.connect_to_local()`.

## Resources

- https://docs.weaviate.io/
- https://docs.weaviate.io/deploy/installation-guides/docker-installation

## Smoke test

`python scripts/smoke.py vectordb/weaviate` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run vectordb/weaviate/smoke.py`); it needs only the Python standard library.
