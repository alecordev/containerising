# Temporal

Temporal server `1.32.2` + Web UI `2.58.1` on PostgreSQL 16. Mirrors the layout of the official [`temporalio/samples-server`](https://github.com/temporalio/samples-server/tree/main/compose) compose setup (`auto-setup` is no longer maintained), with a small schema job and a namespace job. Local development only.

| Service | Role |
|---|---|
| `postgres` | persistence + visibility store (internal) |
| `setup` | one-shot: creates `temporal` / `temporal_visibility` databases and applies schemas (idempotent) |
| `temporal` | frontend/history/matching/worker services in one process (gRPC `7233`) |
| `create-namespace` | one-shot: creates the `default` namespace |
| `ui` | Web UI |
| `worker` | optional example Python worker (profile `worker`) |

## Run

```bash
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete all workflow history
```

- gRPC (SDKs / CLI): `localhost:7233` (`TEMPORAL_PORT`)
- UI: http://localhost:8233 (`TEMPORAL_UI_PORT`; 8233 avoids the usual 8080 clashes)

## Try it with the example worker

```bash
docker compose --profile worker up -d --build worker
docker compose run --rm worker python starter.py "Alice"     # prints: Hello, Alice!
```

Or run the code from your machine (`uv run worker/worker.py` and `uv run worker/starter.py`; dependencies come from the script headers), using `TEMPORAL_ADDRESS=localhost:7233` (the default).

## CLI

No local install needed:

```bash
docker compose run --rm --no-deps --entrypoint temporal create-namespace --address temporal:7233 operator cluster health
docker compose run --rm --no-deps --entrypoint temporal create-namespace --address temporal:7233 workflow list
```

(Any one-shot service from the `temporalio/admin-tools` image works; `temporal` is the CLI.)

## Environment

| Variable | Default |
|---|---|
| `TEMPORAL_VERSION` | `1.32.2` (server and admin-tools) |
| `TEMPORAL_UI_VERSION` | `2.58.1` |
| `TEMPORAL_PORT` / `TEMPORAL_UI_PORT` | `7233` / `8233` |
| `TEMPORAL_NAMESPACE` | `default` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | `temporal` / `temporal` |

## Notes

- `dynamicconfig/development-sql.yaml` contains dev-only dynamic config (do not copy to production).
- Search attributes and advanced visibility use the SQL visibility store; no Elasticsearch required.
- Shell scripts in `scripts/` must keep LF line endings (they are bind-mounted into Linux containers).

## Resources

- https://docs.temporal.io/
- https://github.com/temporalio/samples-server
- https://github.com/temporalio/sdk-python
