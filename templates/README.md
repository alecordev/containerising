# templates/

`templates/service/` is the skeleton for a new service directory. It is a real, working stack (nginx demo), so it passes `python scripts/lint.py` and `python scripts/smoke.py templates/service` as is, which keeps the conventions honest.

## Create a service

```bash
python scripts/new_service.py myservice             # ./myservice
python scripts/new_service.py vectordb/qdrant       # nested; the last segment is the service name
python scripts/new_service.py myservice --docker    # also a Dockerfile + .dockerignore to adapt
```

The skeleton is a runnable stack named `myservice` with variables such as `MYSERVICE_PORT`; the generator replaces `myservice` with your service name and `MYSERVICE` with its upper-case form (`REDPANDA_PORT`).

## What the skeleton contains

| File | Purpose |
|---|---|
| `docker-compose.yml` | No `version:`, pinned image tag as an overridable variable, overridable host port, named volume, a real healthcheck, `restart: unless-stopped` |
| `.env.example` | Every variable with its default (dev-only values); users copy it to `.env` |
| `smoke.py` | Live check: run by `scripts/smoke.py <dir>` (full cycle) or on its own, `python smoke.py` / `uv run smoke.py`, against a running stack. Includes the `smokelib` bootstrap (keep it) |
| `README.md` | Required sections: run, ports, environment variables, credentials, examples, notes, resources |
| `Dockerfile.example`, `.dockerignore.example` | Optional multi-stage Python image: non-root user, `HEALTHCHECK`, whitelist-style ignore file |

## Checklist for a finished template

1. Image tags **pinned and verified** (`docker manifest inspect <image:tag>`); no `:latest` (or `# lint: allow-latest` with the reason).
2. Healthcheck uses a binary that exists in the image: `docker run --rm --entrypoint sh <image> -c "command -v curl wget python3 bash"`. Minimal and distroless images need the product's own CLI, `wget`, or a one-shot probe service. A service that is "not ready" until others join (a hub, a coordinator) needs a liveness check, not a readiness check.
3. Data in **named volumes**; bind mounts only for user content.
4. Host ports overridable; check clashes with `python scripts/ports.py --clashes` and pick a free default with `--free`.
5. `smoke.py` really exercises the service (and cleans up after itself so it can be re-run) and keeps the `sys.path` bootstrap from the skeleton, so it also runs on its own.
6. README complete; `.env.example` present if there are variables; `.dockerignore` next to every Dockerfile.
7. Host-side helpers are **Python** (stdlib). Shell only for scripts that run inside Linux containers. Python examples: put them next to a `requirements.txt` (pinned), run `python scripts/sync_uv.py --add <dir>`, and document them with `uv run <script>`; never `pip install` / `python -m venv` in READMEs (`lint.py` flags it).
8. Add the service to the tables in the root `README.md` and `AGENTS.md`.
9. `python scripts/lint.py` and `python scripts/smoke.py <service>` pass.
