# Meilisearch

[Meilisearch](https://www.meilisearch.com/): fast, typo-tolerant full-text search with a simple REST API. Good for app/site search where Elasticsearch/OpenSearch would be overkill. Runs in **development mode** (built-in search preview at `/`).

## Run

```bash
cd meilisearch
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete the data volume
```

## Ports and URLs

| What | URL | Env override |
|---|---|---|
| REST API + dashboard | http://localhost:7700 | `MEILI_PORT` |

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `MEILI_VERSION` | `v1.56.2` | Image tag |
| `MEILI_ENV` | `development` | `production` requires the master key and disables the dashboard |
| `MEILI_MASTER_KEY` | `dev-master-key-change-me-16b` | Min 16 bytes. API calls send `Authorization: Bearer <key>` |

## Try it

```python
import json, urllib.request

KEY = "dev-master-key-change-me-16b"

def call(method, path, body=None):
    req = urllib.request.Request(
        "http://localhost:7700" + path, method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

call("POST", "/indexes/movies/documents", [{"id": 1, "title": "Carol"}, {"id": 2, "title": "Wonder Woman"}])
# indexing is async: the response contains a taskUid; poll /tasks/<uid> until it succeeds
print(call("POST", "/indexes/movies/search", {"q": "carrol"}))
```

Python (`uv run --with meilisearch python`): `meilisearch.Client("http://localhost:7700", "dev-master-key-change-me-16b")`.

## Notes

- Upgrading across Meilisearch minor versions requires a dump/restore: [docs](https://www.meilisearch.com/docs/learn/update_and_migration/updating).
- Meilisearch also supports hybrid/vector search (embedders), see the docs.

## Resources

- https://www.meilisearch.com/docs
- https://www.meilisearch.com/docs/guides/misc/docker

## Smoke test

`python scripts/smoke.py meilisearch` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run meilisearch/smoke.py`); it needs only the Python standard library.
