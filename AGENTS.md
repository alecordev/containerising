# AGENTS.md

Guidance for AI coding agents (and humans) working in this repo.

## What this repo is

A **library of copy-paste-able Docker / docker compose templates**, one directory per technology, for quick local development and experimentation. It is **not** an application: no build system and no CI. Each top-level directory is independent and self-contained. Everything is **local-dev only** (default passwords, no TLS).

Goals for any change: keep each template **standalone**, **portable** (Linux/macOS/Windows), **configurable via env vars with working defaults**, **pinned**, **minimal**, and **verified by a smoke test**.

## Repository map

Authoritative lists: `python scripts/ports.py` (ports) and each directory's `README.md` (credentials, variables). Image tags are pinned in each compose file; do not rely on versions quoted here.

| Dir | Provides | Main host ports |
|---|---|---|
| `postgresql/`, `postgres_pgadmin/`, `postgres-pgvector/`, `timescaledb/` | PostgreSQL 18 variants (init schema+conf / +pgAdmin / +pgvector built from a pinned source release / TimescaleDB) | 5432 (+5050 pgAdmin) |
| `mysql/`, `mariadb/` | MySQL 8.4 LTS, MariaDB 11.8 LTS | 3306 |
| `sqlserver/`, `oracle-free/`, `cockroachdb/`, `clickhouse/` | SQL Server 2025 Developer, Oracle Free 23ai, CockroachDB, ClickHouse | 1433, 1521, 26257+8080, 8123+9000 |
| `mongo/`, `redis/`, `valkey/`, `cassandra/`, `scylladb/`, `neo4j/`, `orientdb/` | NoSQL / graph stores | 27017+8081, 6379, 6379, 9042, 9042, 7474+7687, 2480+2424 |
| `elasticsearch/`, `opensearch/`, `meilisearch/`, `typesense/` | Search engines (+ Kibana / Dashboards) | 9200+5601, 9200+5602, 7700, 8108 |
| `vectordb/` | `qdrant/`, `weaviate/`, `milvus/`, `chroma/` | 6333, 8080, 19530, 8000 |
| `kafka/` | KRaft (no ZooKeeper): `simple/`, `advanced/` (Kafka UI; `_cluster`: 3 nodes; `_settings`: tuning), `confluent/` (+ Schema Registry); `examples/` | 9092, UI 8090, SR 8081 |
| `redpanda/`, `nats/`, `rabbitmq/`, `debezium/` | Redpanda + Console, NATS JetStream, RabbitMQ 4, Postgres to Kafka CDC | 19092+8085, 4222, 5672+15672, 8083+8085 |
| `airflow/`, `dagster/`, `prefect/`, `temporal/` | Orchestrators (Airflow 3 Celery, Dagster, Prefect 3, Temporal + worker) | 8080, 3000, 4200, 7233+8233 |
| `spark/`, `trino/`, `duckdb/`, `mlflow/`, `jupyterlab/` | Compute and ML tooling | 7077+8080, 8080, none, 5000, 8888 |
| `ollama/`, `langfuse/`, `bi/` | Ollama + Open WebUI + LiteLLM (GPU override file), Langfuse v3, `metabase/` + `superset/` | 11434+3000+4000, 3000, 3000 / 8088 |
| `grafana/`, `observability/` | Grafana+InfluxDB+Telegraf+Prometheus+Alertmanager (cAdvisor/host Telegraf in `host-metrics` profile); LGTM-style Loki+Tempo+Prometheus+OTel Collector | 3000, 8086, 9090, 9093 / 3000, 3100, 3200, 4317-4318 |
| `mailpit/`, `object-storage/`, `localstack/` | SMTP sink; S3 stores `seaweedfs/` + `garage/` (MinIO is archived upstream, see its README); AWS emulation (moto default, real LocalStack under a profile, needs a token) | 1025+8025, 8333 / 3900, 4566 |
| `traefik/`, `caddy/`, `adminer/`, `cloudbeaver/` | Reverse proxies, DB UIs | 80+443+8088, 80+443, 8082, 8978 |
| `wiremock/`, `mockoon/`, `vault/`, `keycloak/`, `gitea/`, `n8n/` | API mocks, secrets (Vault, or OpenBao), OIDC, Git + Actions runner, workflows | 8089, 3001, 8200, 8080+9000, 3001+2222, 5678 |
| `selenium/` | Grid 4.52 (`docker-compose.yml`: hub + chrome/firefox, `edge` profile; `docker-compose.standalone.yml`: `BROWSER=chrome|firefox|edge`), `src/`, `summary/`, `utils/` | 4444, VNC 7900 |
| `wikipedia/` | Local Wikipedia: Kiwix server + Python downloader (`prep/wiki.py`), data under `./data` | 8099 |
| `lamp/`, `wordpress/` | PHP 8.4 Apache + MariaDB (own Dockerfile); WordPress + MySQL | 8080, 8000+3306 |
| `python/` | Dockerfile patterns on `python:3.14-slim-trixie`: `multi_stage`, `multi_stage_gcc`, `multi_stage_streamlit` (FastAPI + Streamlit), `plain_django`, `plain_flask_gunicorn`, `plain_multi_stage` | 8000, 8081, 8501 |
| `all/` | RabbitMQ, Redis, Elasticsearch + Kibana, Postgres + pgAdmin, Mongo + Mongo Express in one compose, with Python `examples/` | see ports tool |
| `scripts/` | Python tooling: `smoke.py`, `smokelib.py`, `lint.py`, `ports.py`, `new_service.py` (see `scripts/README.md`) | n/a |
| `templates/` | `service/` skeleton used by `new_service.py` | n/a |

Typical service layout: `docker-compose.yml`, optional `Dockerfile` + `.dockerignore`, `.env.example`, `README.md`, `smoke.py`, mounted config, optional `examples/`.

## Working with a service

Run commands **from inside the service directory** (paths are relative to it). Compose v2:

```bash
cd <service>
docker compose up -d --wait   # blocks until healthchecks pass
docker compose logs -f <svc>
docker compose down           # add -v to also delete named volumes
```

Profiles: `--profile edge` (selenium), `host-metrics` (grafana), `flower` (airflow), `worker` (prefect), `gpu`/override file for ollama, `demo` (adminer). Python examples: use a venv, `pip install -r requirements.txt`.

## Tooling (Python only)

```bash
python scripts/lint.py                     # static checks (compose config, tags, docs coverage, ...)
python scripts/smoke.py <dir> [<dir>...]   # up --wait, run smoke.py, down -v (project "smoke" only)
python scripts/smoke.py --list
python <dir>/smoke.py                      # (or: uv run <dir>/smoke.py) just the check, against a stack you already started
python scripts/ports.py --clashes          # host-port clashes; --free 8000-8100 to pick a free one
python scripts/new_service.py <name>       # scaffold from templates/service
python scripts/sync_uv.py [--check|--add DIR|--lock]   # uv projects and script headers from requirements.txt
```

**Rule: host-side tooling and helper scripts are Python 3.10+ standard library, never bash/PowerShell/batch** (run them with `python` or `uv run`; each carries a PEP 723 header so uv picks a suitable interpreter) (cross-OS, no hidden GNU-tool or path-conversion dependencies). Shell is acceptable only for scripts that execute **inside a Linux container** whose image ships no Python (e.g. `temporal/scripts/*.sh`), referenced from compose, with a one-line comment saying why; `.gitattributes` keeps them LF. READMEs use plain `docker compose ...` commands or Python so they work in PowerShell, cmd and bash alike (no `$(...)`, `export`, `&&` chains or pipes to grep).

## Conventions

1. **One directory = one template**; no cross-directory dependencies. `all/` intentionally duplicates other templates.
2. **No `version:` key** in compose files; **pinned image tags**, verified to exist (`docker manifest inspect <image:tag>`); no `:latest` (exception: `# lint: allow-latest` plus the reason on that line, e.g. an image that only publishes `latest`). Tags/versions are env-overridable (`${PG_VERSION:-18.6}`).
3. **Config via env vars with defaults** (`${POSTGRES_PASSWORD:-postgres}`), host ports overridable (`"${PG_PORT:-5432}:5432"`). Variables documented in the README and a committed `.env.example`. Real `.env` is git-ignored; never commit secrets.
4. **Data**: databases/brokers use **named volumes**; bind mounts only for user content (`./notebooks`, `./dags`, `./www`, `./data`). `.gitignore` covers `.docker/`, `data/`, `logs/`, `*.zim`, partial downloads.
5. **Healthchecks** on every long-running service and `depends_on: condition: service_healthy`. Verify the binary exists in the image (`docker run --rm --entrypoint sh <img> -c "command -v curl wget python3 bash"`); many images lack curl/wget (cp-schema-registry has only python3; Loki/Tempo are distroless). A service that is "not ready" until others join (Selenium hub) needs a liveness check, not a readiness check (this deadlocked `depends_on` once).
6. `restart: unless-stopped` for long-running services; no `links:`, no static IPs, no hardcoded host IPs.
7. **Dockerfiles**: multi-stage where useful, non-root `USER`, `ENV KEY=value`, `--no-cache-dir`, `--no-install-recommends` + apt list cleanup, `HEALTHCHECK` for servers, no secrets in layers, base `python:3.14-slim-trixie` for Python.
8. **`.dockerignore`** next to every Dockerfile (whitelist style where the context is large, e.g. `wikipedia/`, `postgres-pgvector/`; BuildKit per-Dockerfile `Dockerfile.dockerignore` in `python/multi_stage_streamlit`). If a `COPY` needs a file the ignore file excludes, fix the ignore file.
9. **Every template has a `smoke.py`** (or `smoke.<compose-stem>.py`) that really exercises the service and cleans up after itself; written with `scripts/smokelib.py`. It starts with the 3-line `sys.path` bootstrap from `templates/service/smoke.py` (finds `scripts/` from any depth) and a generated PEP 723 header, so it runs on its own against a running stack (`python <dir>/smoke.py` or `uv run <dir>/smoke.py`, from any directory, reading the directory's `.env`) as well as under the runner. `lint.py` enforces the bootstrap. Services that exit by design carry a `.smoke-skip` file.
10. Each service has a `README.md`: run, ports/URLs, credentials, env vars, usage examples, caveats, resources. `lint.py` fails if a top-level service directory is missing from the root `README.md` or this file.
11. **Python examples use uv.** Small, runnable, deps pinned in a local `requirements.txt` (the single source of truth, still used by pip and Docker builds), connection settings from env vars. Register the directory with `python scripts/sync_uv.py --add <dir>`: that generates `pyproject.toml` (`uv sync` / `uv run python x.py`) and a PEP 723 header in each script (`uv run x.py`). Never edit those generated parts; `lint.py` fails when they drift. READMEs show `uv run`, `uv run --with <pkg> python` (one-off snippets) or `uv add`, never `pip install` / `python -m venv`. `requires-python` defaults to `>=3.11`.
12. Root `.gitignore` and `.gitattributes` are the only ignore/attribute files (exception: `selenium/src/*/output/.gitignore` placeholder).

## Lessons from running every stack (check these in new templates)

- **`localhost` in a healthcheck**: busybox `wget` resolves `localhost` to `::1` first. Servers that listen on IPv4 only (ClickHouse) look dead. Use `127.0.0.1`. Servers started with an explicit bind/advertise address (`weed -ip=seaweedfs`) listen only on that address: probe it, not `localhost`.
- **Init-phase "healthy"**: the official MySQL image runs a socket-only temporary server during first boot, so `mysqladmin ping -h localhost` reports healthy too early; ping `-h 127.0.0.1` (TCP) instead.
- **SQLAlchemy 2.1** maps `postgresql://` to the psycopg v3 driver. Images that ship psycopg2 (Dagster, MLflow) need `postgresql+psycopg2://` explicitly.
- **Dependencies you forgot to declare**: Dagster's gRPC code server needs Postgres to be healthy before it starts. If a service loads a DB at startup, add `depends_on: <db>: condition: service_healthy`.
- **Config files change shape between majors**: Redpanda Console v3 wants `schemaRegistry` at the top level, not under `kafka`. Caddy directive order: a bare `respond` loses to a catch-all `handle`; give it its own `handle` block.
- **Entrypoint overrides**: `entrypoint: ["sh"]` turns `run nats-box nats ...` into `sh nats ...`. Keep the image entrypoint unless a shell is the point.
- **Breaking defaults**: ScyllaDB creates keyspaces with tablets, which reject `SimpleStrategy` (use `NetworkTopologyStrategy`); RabbitMQ 4 rejects transient non-exclusive queues (declare them durable); the gvenzl Oracle faststart image already ships `FREEPDB1`, so setting `ORACLE_DATABASE=FREEPDB1` makes it restart-loop (ORA-65012), and its init scripts run in the CDB root (`ALTER SESSION SET CONTAINER = FREEPDB1` first).
- **Cluster listeners**: in a multi-broker Kafka compose, a client inside one container must use the INTERNAL listeners of all brokers (`kafka-1:19092,...`); a bootstrap of `localhost:9092` gets redirected to host-facing addresses that do not exist there.
- **Variables that hide behaviour**: `REDISCLI_AUTH` in the container makes `redis-cli` authenticate by itself, so "anonymous access is refused" tests must clear it.
- **First start is slow**: Langfuse and Airflow run migrations on first boot (minutes). Give healthchecks a long `start_period` and generous `retries`.
- **Lock early**: running `uv lock` on the legacy `requirements.txt` files found an unsatisfiable pin (`neo4j>=6.4` vs `neomodel 7` which pins the driver to 6.1.x) that plain pip would also have failed on. Run `python scripts/sync_uv.py --lock` after changing requirements.
- **Ports on a developer machine**: other projects' containers hold common ports (3100, 3200, 8000 here). Re-run with port overrides (`WEB_PORT=18000 python scripts/smoke.py ...`); `smoke.py` passes the environment through to compose and to the smoke test.

## Default credentials (dev only)

Authoritative per service: its `README.md` and `.env.example`. Common ones:

| Service | Credentials |
|---|---|
| Postgres | `postgres` / `postgres` (Prefect's own: `prefect` / `prefect`) |
| pgAdmin | `pgadmin@pgadmin.org` / `admin` |
| Mongo / Mongo Express | `admin` / `admin` |
| RabbitMQ | `guest`/`guest` in `all/`; `admin`/`admin` in `rabbitmq/` |
| Redis | password `password` |
| Neo4j | `neo4j` / `password` (min 8 chars) |
| OrientDB | `root` / `root` |
| MariaDB / MySQL | root `root`; app users per README |
| Airflow | `airflow` / `airflow` |
| Grafana | `admin` / `admin`; InfluxDB `admin` / `adminadmin` |
| Selenium VNC | `secret` |
| Jupyter | empty token on `127.0.0.1`; set `JUPYTER_TOKEN` |
| Others (Keycloak, Gitea, Vault, n8n, Langfuse, SQL Server, Oracle, ...) | see the service README |

## Caveats

- **Port clashes**: many templates share standard ports (3000, 5432, 6379, 8000, 8080, 8081, 9092, 9200, 27017, ...). Run `python scripts/ports.py --clashes`; run clashing ones one at a time or override the port variable.
- **Corporate proxy with TLS inspection** (as on the development machine): containers cannot reach the internet without your CA, and Windows `curl` fails revocation checks (`--ssl-no-revoke`). Fetch data on the host with Python (`wikipedia/prep/wiki.py` uses the OS trust store and `HTTPS_PROXY`) and mount it. Some images' telemetry calls fail harmlessly (e.g. Qdrant).
- **Typesense** server segfaults at startup on the Windows 11 / Docker Desktop WSL2 host used for development (documented in its README); its smoke test is expected to fail there.
- **Ollama** model download fails behind a TLS-inspecting proxy (container does not trust the CA); see its README for workarounds.
- **Elasticsearch/OpenSearch** on Linux need `vm.max_map_count=262144`.
- **Heavy stacks**: Oracle Free, SQL Server (2 GB RAM, EULA), Milvus, Cassandra, Langfuse, Airflow, Spark and the large Wikipedia sets. Check requirements in each README before running them.
- **Grafana `host-metrics` profile** (cAdvisor/host Telegraf) bind-mounts host `/`, `/proc`, `/sys` and the Docker socket: Linux only and security-sensitive. **Traefik** mounts the Docker socket read-only.
- **MinIO** is not shipped (upstream archived, images gone); use `object-storage/seaweedfs` or `garage`. **LocalStack** now needs an auth token for the real image; `localstack/` defaults to moto.
- **uv behind a TLS-inspecting proxy**: uv ships its own CA roots; set `UV_NATIVE_TLS=1` (or `--native-tls`) to use the OS certificate store.
- **Windows**: bind-mounted files that run inside containers must be LF (`.gitattributes` enforces it). A mangled bind-mount path once created a directory named `scripts;C`; `.gitignore` ignores `*;*` and `lint.py` flags odd names.

## Verification status

`python scripts/smoke.py` is the source of truth. Last full run (2026-11-13, Windows 11 + Docker Desktop on WSL2, behind a TLS-inspecting corporate proxy, 73 compose targets, run sequentially):

- **71 of 73 pass** end to end: stack becomes healthy, then its `smoke.py` writes and reads real data. Several stacks needed fixes found by this run (see "Lessons from running every stack"); each was re-run and now passes.
- **`typesense`**: the server segfaults at startup on this host (documented in its README); not a template defect, untested here.
- **`ollama`**: the stack starts, but `model-pull` cannot download models through the proxy (`x509: certificate signed by unknown authority`); untested end to end here.
- Port clashes with other containers on the machine (3100, 3200, 8000) were worked around with port overrides (`LOKI_PORT`, `TEMPO_PORT`, `WEB_PORT`, `CHROMA_PORT`, `WORDPRESS_PORT`); the templates themselves use the standard ports.
- `python scripts/lint.py` (including `docker compose config` for every compose file) passes.

uv (2026-11-13): all 16 uv projects were locked and installed (`uv sync`), every example script compiled and its PEP 723 header resolved; the Neo4j (driver + neomodel), MongoDB and Redis examples were run against live containers with `uv run`, both as scripts and inside the project environment. The other examples were verified up to installing their dependencies and compiling, not run against live services.

Not exercised: the optional profiles (`host-metrics`, `flower`, `worker`, `edge`, `gpu`, `demo`), the Python example scripts under `*/examples` and `*/src` against live services (they compile and use current APIs), `selenium/src/simple-*` beyond building the images, and anything on a Linux host (cAdvisor, `vm.max_map_count`, file ownership of bind mounts).

## Git hygiene

- `python scripts/lint.py`, `git status --short` and `git ls-files -ci --exclude-standard` before committing.
- `docker-compose.override.yml` is ignored on purpose, for personal tweaks.
- Large datasets (`*.zim`, `wikipedia/data/`) are ignored.
- Commit messages in history are short and imperative.

## Adding a new service template

```bash
python scripts/new_service.py <name> [--docker]
```

Then edit the generated `docker-compose.yml`, `README.md`, `.env.example`, `smoke.py`; pick a free default port (`python scripts/ports.py --free 8000-8100`); add rows to the tables in `README.md` and this file; run `python scripts/lint.py` and `python scripts/smoke.py <name>`. Full checklist: `templates/README.md`.
