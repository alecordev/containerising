# Langfuse

Self-hosted [Langfuse](https://langfuse.com) (LLM tracing, prompts, evals), adapted from the official compose file and trimmed for local use.

| Service | Image | Purpose |
|---|---|---|
| `langfuse-web` | `docker.langfuse.com/langfuse/langfuse:4.79` | UI + API (port 3000) |
| `langfuse-worker` | `docker.langfuse.com/langfuse/langfuse-worker:4.79` | async ingestion |
| `postgres` | `postgres:17-alpine` | transactional data |
| `clickhouse` | `clickhouse/clickhouse-server:26.3.62.3` | traces and observations |
| `redis` | `redis:7.2-alpine` | queues and cache |
| `minio` | `cgr.dev/chainguard/minio:latest` | S3 storage for events and media |

## Run

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down      # add -v to delete all data
```

First start takes a minute (database and ClickHouse migrations).

- UI: http://localhost:3000, login `admin@example.com` / `changeme123`
- Project API keys (bootstrapped): public `pk-lf-local`, secret `sk-lf-local`
- MinIO console: http://localhost:9091 (`minio` / `miniosecret`, bound to localhost)

Only the web UI and the MinIO S3 port (9090, used by the browser for media upload) are published; every other service stays on the internal network.

## Send a trace

Langfuse v4 ingests traces over OpenTelemetry. Raw HTTP from Python (standard library only; HTTP basic auth with the project keys), then read the span back:

```python
import base64, json, secrets, time, urllib.request

auth = "Basic " + base64.b64encode(b"pk-lf-local:sk-lf-local").decode()
trace_id, span_id, now = secrets.token_hex(16), secrets.token_hex(8), time.time_ns()
span = {"resourceSpans": [{"scopeSpans": [{"scope": {"name": "demo"}, "spans": [{
    "traceId": trace_id, "spanId": span_id, "name": "hello", "kind": 1,
    "startTimeUnixNano": str(now - 10**9), "endTimeUnixNano": str(now)}]}]}]}

def call(path, body=None):
    req = urllib.request.Request("http://localhost:3000" + path, json.dumps(body).encode() if body else None,
        {"Content-Type": "application/json", "Authorization": auth, "x-langfuse-ingestion-version": "4"})
    return urllib.request.urlopen(req).read().decode()

call("/api/public/otel/v1/traces", span)
time.sleep(15)   # ingestion is asynchronous: web -> worker -> ClickHouse
print(call(f"/api/public/v2/observations?traceId={trace_id}"))
```

The legacy read endpoints (`/api/public/traces`, `/observations`, `/scores`) return 404 in v4 events-only mode; use the v2 observations API or the UI.

With the Python SDK (save the snippet as `trace.py` and run `uv run --with langfuse trace.py`):

```python
import os
os.environ.update(LANGFUSE_HOST="http://localhost:3000",
                  LANGFUSE_PUBLIC_KEY="pk-lf-local", LANGFUSE_SECRET_KEY="sk-lf-local")
from langfuse import observe

@observe()
def answer(q: str) -> str:
    return "42"

answer("meaning of life?")
```

Pairs well with [`../ollama`](../ollama) (LiteLLM can send traces here via its Langfuse callback).

## Environment

Everything is in `.env.example`. Key variables:

| Variable | Default |
|---|---|
| `LANGFUSE_VERSION` | `4.79` (web and worker share one tag) |
| `LANGFUSE_PORT` / `NEXTAUTH_URL` | `3000` / `http://localhost:3000` |
| `NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY` | dev-only placeholders, **change them** |
| `POSTGRES_*`, `CLICKHOUSE_*`, `REDIS_AUTH`, `MINIO_ROOT_*` | dev-only passwords |
| `LANGFUSE_INIT_*` | org / project / keys / user created on first start (empty to disable) |

## Notes

- ClickHouse and the worker want ~4 GB RAM in total; the whole stack idles around 3 GB.
- `LANGFUSE_INIT_*` only applies when the database is empty; after changing them use `docker compose down -v`.
- `cgr.dev/chainguard/minio` only publishes `latest` on Chainguard's free tier, so it is the one unpinned image in this repo (marked `# lint: allow-latest`). Swap in any S3-compatible service (for example [`../object-storage`](../object-storage)) by editing the `minio` service and the `LANGFUSE_S3_*` variables.
- Generate your own secrets with `python -c "import secrets; print(secrets.token_hex(32))"` (for `ENCRYPTION_KEY`, `SALT`, `NEXTAUTH_SECRET`).
- Self-hosting reference: https://langfuse.com/self-hosting

## Verify

`python ../scripts/smoke.py langfuse` brings the stack up, runs `smoke.py` (ingests a trace with the bootstrapped keys and reads it back from ClickHouse) and tears it down. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run langfuse/smoke.py`).

