# Typesense

[Typesense](https://typesense.org/): open-source, typo-tolerant search engine (in-memory index, simple API, built-in vector search). A lightweight alternative to Elasticsearch/Algolia.

## Run

```bash
cd typesense
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete the data volume
```

## Ports and URLs

| What | URL | Env override |
|---|---|---|
| REST API | http://localhost:8108 | `TYPESENSE_PORT` |

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `TYPESENSE_VERSION` | `30.2` | Image tag |
| `TYPESENSE_API_KEY` | `dev-typesense-key` | Admin key; send as `X-TYPESENSE-API-KEY` |

## Try it

```python
import json, urllib.request

KEY = "dev-typesense-key"

def call(method, path, body=None):
    req = urllib.request.Request(
        "http://localhost:8108" + path, method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={"X-TYPESENSE-API-KEY": KEY, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

call("POST", "/collections", {"name": "books", "fields": [{"name": "title", "type": "string"}]})
call("POST", "/collections/books/documents", {"title": "Dune"})
print(call("GET", "/collections/books/documents/search?q=dnue&query_by=title"))   # typo-tolerant
print(call("GET", "/health"))
```

Python: `uv run --with typesense python`.

## Troubleshooting

- **Container exits immediately with code 139 (segfault) and no logs.** Seen when testing on a Windows 11 + Docker Desktop (WSL2) machine: `typesense-server` crashed even for `--version`, on 29.1, 30.1 and 30.2, so it is not specific to this compose file. The compose file and image are the officially documented ones. Try another host or Docker backend, or use [meilisearch](../meilisearch) / [opensearch](../opensearch) instead. Check with `docker run --rm typesense/typesense:30.2 --version`.

## Notes

- The image ships `bash` but no curl/wget, so the healthcheck probes `/health` through bash's `/dev/tcp`.
- Typesense keeps the whole index in RAM; size the container accordingly.
- `--enable-cors` is on for local front-end experiments; remove it for anything else.

## Resources

- https://typesense.org/docs/
- https://typesense.org/docs/guide/install-typesense.html#docker

## Smoke test

`python scripts/smoke.py typesense` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run typesense/smoke.py`); it needs only the Python standard library.
