# BI tools

Two open-source business-intelligence stacks, each self-contained in its own directory:

| Directory | Tool | Default URL | Login | Weight |
|---|---|---|---|---|
| [`metabase/`](metabase) | Metabase | http://localhost:3000 | setup wizard on first visit | light: app + Postgres, ~1.5 GB RAM |
| [`superset/`](superset) | Apache Superset | http://localhost:8088 | `admin` / `admin` | heavier: app + Postgres + Redis, ~2 GB RAM |

Pick Metabase for quick questions, dashboards and embedding with minimal setup; pick Superset for SQL Lab, a larger chart library and fine-grained semantic layers.

## Run

```bash
cd metabase        # or: cd superset
docker compose up -d --wait     # copy .env.example to .env first to override defaults (optional)
docker compose down             # add -v to delete all state
```

Verify either one with `python scripts/smoke.py bi/metabase` / `bi/superset` from the repo root. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run bi/smoke.py`).

## Pointing them at your data

Both run in containers, so `localhost` inside them means the container itself. To query a database from another template in this repo:

- Use `host.docker.internal` plus the published port (works on Docker Desktop; on Linux add `extra_hosts: ["host.docker.internal:host-gateway"]`), e.g. Postgres from [`../postgresql`](../postgresql) at `host.docker.internal:5432`.
- Or attach the BI service to the other stack's Docker network and use the service name as host.

Good pairings: [`../postgresql`](../postgresql), [`../clickhouse`](../clickhouse), [`../trino`](../trino), [`../mongo`](../mongo).

## Ports

Metabase and Superset use different default ports, but port 3000 is shared with Open WebUI ([`../ollama`](../ollama)) and Langfuse ([`../langfuse`](../langfuse)); override with `METABASE_PORT` / `SUPERSET_PORT`.
