# Chroma

[Chroma](https://www.trychroma.com/): simple, developer-friendly embedding database. The easiest vector store to start with for prototyping RAG apps. This template runs the Chroma server with persistence and **no authentication**.

## Run

```bash
cd vectordb/chroma
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete the data volume
```

## Ports and URLs

| What | URL | Env override |
|---|---|---|
| HTTP API | http://localhost:8000 | `CHROMA_PORT` |
| Heartbeat | http://localhost:8000/api/v2/heartbeat | |
| OpenAPI docs | http://localhost:8000/docs | |

Port 8000 collides with the wordpress and Django templates; override `CHROMA_PORT` when running them together.

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `CHROMA_VERSION` | `1.5.9` | Image tag |
| `CHROMA_PORT` | `8000` | Host port |

## Try it

Run the snippet with `uv run --with chromadb python snippet.py`.

```python
import chromadb
client = chromadb.HttpClient(host="localhost", port=8000)
col = client.get_or_create_collection("demo")
col.add(ids=["1", "2"], embeddings=[[0.1, 0.2, 0.3, 0.4], [0.9, 0.1, 0.1, 0.1]], documents=["a", "b"])
print(col.query(query_embeddings=[[0.1, 0.2, 0.3, 0.4]], n_results=1))
```

Raw REST (v2): `curl localhost:8000/api/v2/heartbeat`; collections live under `/api/v2/tenants/default_tenant/databases/default_database/collections`.

## Resources

- https://docs.trychroma.com/
- https://docs.trychroma.com/guides/deploy/docker

## Smoke test

`python scripts/smoke.py vectordb/chroma` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run vectordb/chroma/smoke.py`); it needs only the Python standard library.
