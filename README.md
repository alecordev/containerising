# Containers

Ready-to-run `Dockerfile`s and `docker compose` stacks for databases, brokers, search, data and AI tooling, observability and dev utilities. Each top-level directory is an independent, self-contained template for **local development**: copy it, `cd` into it, run it.

- Requires Docker Engine with the Compose v2 plugin (`docker compose`).
- Python examples and snippets use [uv](https://docs.astral.sh/uv/) (`uv run ...`); `requirements.txt` stays for pip and Docker builds. Repo tooling (`scripts/`) is **Python 3.10+, standard library only**, so `python scripts/...` (or `uv run scripts/...`) works the same on Linux, macOS and Windows.
- Conventions, ports, default credentials and caveats for contributors and AI agents: [AGENTS.md](AGENTS.md).

## Quick start

```bash
cd postgres_pgadmin
docker compose up -d --wait       # waits for healthchecks
docker compose logs -f
docker compose down               # add -v to delete the data volumes
```

Every variable has a working default; to change them copy `.env.example` to `.env` (where one exists) or set them in your shell. Host ports are overridable, e.g. `PG_PORT=5433 docker compose up -d`. Many templates use the products' standard ports, so run clashing ones one at a time or override the port (see [Ports](#ports)).

## Templates

### Relational and NoSQL databases

| Directory | Contents |
|---|---|
| `postgresql/` | PostgreSQL 18 with init schema and an active `postgres.conf` |
| `postgres_pgadmin/` | PostgreSQL 18 + pgAdmin |
| `postgres-pgvector/` | PostgreSQL 18 + pgvector (multi-stage build, pinned version) |
| `timescaledb/` | TimescaleDB (PostgreSQL 18) with a sample hypertable |
| `mysql/` | MySQL 8.4 LTS |
| `mariadb/` | MariaDB 11.8 LTS |
| `sqlserver/` | Microsoft SQL Server 2025 (Developer) |
| `oracle-free/` | Oracle Database Free 23ai (faststart image) |
| `cockroachdb/` | CockroachDB single node |
| `clickhouse/` | ClickHouse (analytics) |
| `mongo/` | MongoDB 8 + Mongo Express |
| `redis/` | Redis 8 |
| `valkey/` | Valkey 9 (Redis-compatible) |
| `cassandra/` | Apache Cassandra 5 |
| `scylladb/` | ScyllaDB |
| `neo4j/` | Neo4j with APOC |
| `orientdb/` | OrientDB distributed pair |

### Search and vector databases

| Directory | Contents |
|---|---|
| `elasticsearch/` | Elasticsearch + Kibana 9 |
| `opensearch/` | OpenSearch + Dashboards 3 |
| `meilisearch/` | Meilisearch |
| `typesense/` | Typesense |
| `vectordb/` | `qdrant/`, `weaviate/`, `milvus/`, `chroma/` (see `vectordb/README.md`) |

### Messaging and streaming

| Directory | Contents |
|---|---|
| `kafka/` | KRaft Kafka: `simple/`, `advanced/` (Kafka UI, 3-node cluster, tuning variant), `confluent/` (+ Schema Registry) |
| `redpanda/` | Redpanda + Console |
| `nats/` | NATS with JetStream |
| `rabbitmq/` | RabbitMQ 4 + management UI |
| `debezium/` | Change data capture: Postgres to Kafka via Debezium Connect |

### Data, ML and AI

| Directory | Contents |
|---|---|
| `airflow/` | Apache Airflow 3 (Celery, Postgres, Redis) |
| `dagster/` | Dagster webserver, daemon and example code location |
| `prefect/` | Prefect 3 server |
| `temporal/` | Temporal server + UI + example Python worker |
| `spark/` | Apache Spark 4 master + workers |
| `trino/` | Trino with TPC-H and memory catalogs |
| `duckdb/` | DuckDB image with example SQL |
| `mlflow/` | MLflow tracking server on Postgres |
| `jupyterlab/` | JupyterLab image |
| `ollama/` | Ollama + Open WebUI + LiteLLM gateway (optional GPU override) |
| `langfuse/` | Langfuse LLM observability (self-hosted v3 stack) |
| `bi/` | `metabase/` and `superset/` (see `bi/README.md`) |

### Observability

| Directory | Contents |
|---|---|
| `grafana/` | Grafana, InfluxDB, Telegraf, Prometheus, Alertmanager (+ cAdvisor, host Telegraf on Linux) |
| `observability/` | Grafana + Loki + Tempo + Prometheus + OpenTelemetry Collector |

### Dev platform and tools

| Directory | Contents |
|---|---|
| `mailpit/` | Fake SMTP server with web UI |
| `object-storage/` | S3-compatible stores: `seaweedfs/`, `garage/` (MinIO status explained in its README) |
| `localstack/` | Local AWS APIs (moto by default; real LocalStack behind a profile) |
| `traefik/` | Reverse proxy with Docker routing and a demo service |
| `caddy/` | Reverse proxy with automatic local HTTPS |
| `adminer/` | Database UI that can join other templates' networks |
| `cloudbeaver/` | Web database IDE |
| `wiremock/` | HTTP API mocking |
| `mockoon/` | HTTP API mocking (Mockoon CLI) |
| `vault/` | HashiCorp Vault (dev mode and persistent mode; OpenBao alternative) |
| `keycloak/` | Keycloak with an importable demo realm |
| `gitea/` | Gitea + optional Actions runner |
| `n8n/` | n8n workflow automation |
| `selenium/` | Selenium Grid, standalone browsers, Python examples |

### Applications and references

| Directory | Contents |
|---|---|
| `wikipedia/` | **Local Wikipedia** served by Kiwix, with an automated, verified, resumable Python downloader |
| `lamp/` | PHP 8.4 Apache + MariaDB |
| `wordpress/` | WordPress + MySQL |
| `python/` | Dockerfile patterns: multi-stage, gcc wheels, FastAPI + Streamlit, Django, Flask |
| `all/` | RabbitMQ, Redis, Elasticsearch + Kibana, Postgres + pgAdmin, Mongo + Mongo Express in one compose |

## Python examples (uv)

Every directory with host-run Python examples is a uv project:

```bash
uv run path/to/script.py      # zero setup: the script's PEP 723 header lists its dependencies
cd <dir> && uv sync           # or build the project environment from pyproject.toml, then: uv run python script.py
uv run --with <package> python    # one-off snippets from the READMEs (pymongo, qdrant-client, ...)
```

`requirements.txt` is the **single source of truth** (pip and Docker builds still use it). `pyproject.toml` and the script headers are generated from it by `python scripts/sync_uv.py`, and `scripts/lint.py` fails if they drift. Behind a TLS-inspecting proxy set `UV_NATIVE_TLS=1` (or pass `--native-tls`) so uv uses the OS certificate store.

## Tooling (`scripts/`, Python only)

| Command | What it does |
|---|---|
| `python scripts/smoke.py [targets]` | Brings each stack up (`--wait`), runs its `smoke.py` live check, tears it down. `--list`, `--rmi` (save disk), `--keep`, `-x` to exclude. Each `<dir>/smoke.py` also runs on its own against a stack you started: `python <dir>/smoke.py` or `uv run <dir>/smoke.py`, from any directory |
| `python scripts/lint.py [--no-docker]` | Static checks: `compose config`, no `version:`/`:latest`, Python compiles, `.dockerignore` and README present, odd names, docs coverage |
| `python scripts/sync_uv.py [--check]` | Regenerates each uv project's `pyproject.toml` and the PEP 723 script headers from `requirements.txt`; `--add DIR` registers a new project, `--lock` refreshes `uv.lock` files |
| `python scripts/ports.py [--clashes]` | Port map and clashes; `--free 8000-8100` finds unused ports |
| `python scripts/new_service.py <name> [--docker]` | Creates a new service from `templates/service` |

Details in [scripts/README.md](scripts/README.md) and [templates/README.md](templates/README.md).

## Ports

Many templates publish the product's standard port. Run `python scripts/ports.py --clashes` for the current list; the usual ones are 3000, 5432, 6379, 8000, 8080, 8081, 9092, 9200 and 27017. Every host port is a variable (`${PG_PORT:-5432}`), so `PG_PORT=5433 docker compose up -d` avoids a clash.

## Troubleshooting

- **Behind a corporate proxy** with TLS inspection: containers usually cannot reach the internet. Download datasets on the host (for example `uv run wikipedia/prep/wiki.py download`) and mount the directory.
- **Windows**: use Docker Desktop with WSL2. Database data lives in named volumes (fast, no permission problems). Shell snippets in READMEs are plain `docker compose` commands or Python so they work in PowerShell, cmd and bash.
- **Linux**: Elasticsearch/OpenSearch need `vm.max_map_count=262144`; bind-mounted data directories must be writable by the container user.
- **Disk and memory**: Oracle, SQL Server, Milvus, Cassandra, Langfuse, Airflow and the large Wikipedia sets need several GB; the READMEs state requirements.

## Clean up

```bash
docker compose down -v --remove-orphans     # one stack, deleting its volumes
docker system prune -a --volumes            # EVERYTHING unused on this host (destructive)
```

## Adding a template

```bash
python scripts/new_service.py myservice
# edit docker-compose.yml, README.md, smoke.py
python scripts/smoke.py myservice
python scripts/lint.py
```

Then add a row to the tables above and in [AGENTS.md](AGENTS.md); `lint.py` fails if a service directory is undocumented.
