# Dagster

Dagster 1.13 (`dagster`, `dagster-webserver`, `dagster-postgres` pinned in `requirements.txt`) with PostgreSQL 18 for run/event/schedule storage. Local development only.

Three Dagster roles run from one locally built image (`Dockerfile`, `python:3.13-slim-trixie`, non-root user):

| Service | Role |
|---|---|
| `user-code` | gRPC server hosting your code location (`pipeline.definitions`) |
| `webserver` | UI + GraphQL API (`dagster-webserver`) |
| `daemon` | schedules, sensors and the run queue (`dagster-daemon`) |
| `postgres` | instance storage (not published to the host) |

## Run

```bash
# Optional: copy .env.example to .env to override defaults
docker compose up -d --build --wait
docker compose down    # add -v to delete the database and run storage
```

- UI: http://localhost:3000 (`DAGSTER_PORT`)
- GraphQL playground: http://localhost:3000/graphql

> Port 3000 is also the default of `grafana/` and `observability/`. Set `DAGSTER_PORT=3001` (or the other port) to run them together.

## Try it

Open the UI, go to **Jobs → all_assets_job → Launchpad → Launch run**, or **Assets → Materialize all**. The example schedule (`every_minute`) is off by default; enable it under **Automation**.

## Add your own code

Edit/replace `pipeline/definitions.py` (keep `defs = dg.Definitions(...)`), add dependencies to `requirements.txt`, then:

```bash
docker compose up -d --build user-code webserver daemon
```

To load a second code location, add another `grpc_server` entry to `workspace.yaml` and another service running `dagster api grpc`.

Instance settings (queue size, storage) live in `dagster.yaml`; telemetry is disabled.

## Environment

| Variable | Default |
|---|---|
| `DAGSTER_PORT` | `3000` |
| `DAGSTER_PG_USERNAME` / `DAGSTER_PG_PASSWORD` / `DAGSTER_PG_DB` | `dagster` |

## Notes

- Runs are launched by the daemon through the default run launcher inside the `user-code` container (no Docker socket needed). Compute logs go to the shared `dagster-storage` volume so the webserver can display them.
- `docker compose exec webserver dagster --version` prints the installed version.

## Resources

- https://docs.dagster.io/
- https://github.com/dagster-io/dagster/tree/master/examples/deploy_docker
