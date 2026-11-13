# All-in-one local stack

RabbitMQ, Redis, Elasticsearch + Kibana, PostgreSQL + pgAdmin, MongoDB + Mongo Express in one compose file.

## Running locally

1. Ensure Docker with Compose v2 (`docker compose`) is available.
2. Optional: copy `.env.example` to `.env` and edit. Every variable has a default, so this is not required.
3. `docker compose up -d` — or start only what you need: `docker compose up -d redis postgres`.
4. `docker compose down` to stop (`-v` also deletes all data volumes).

Requires roughly 4 GB of free RAM when Elasticsearch is included (`ES_HEAP` tunes its heap).

## Services

| Service | Image | URL / port | Default credentials |
|---|---|---|---|
| RabbitMQ | `rabbitmq:4.3-management-alpine` | amqp `5672`, UI http://localhost:15672 | `guest` / `guest` |
| Redis | `redis:8.8-alpine` | `6379` | password `password` |
| Elasticsearch | `elasticsearch:9.5.6` | http://localhost:9200 | security disabled (dev only) |
| Kibana | `kibana:9.5.6` | http://localhost:5601/app/home | - |
| PostgreSQL | `postgres:18.6-alpine` | `5432` | `postgres` / `postgres` |
| pgAdmin | `dpage/pgadmin4:9.19` | http://localhost:5050 | `pgadmin@pgadmin.org` / `admin` |
| MongoDB | `mongo:8.0` | `27017` | `admin` / `admin` |
| Mongo Express | `mongo-express:1.0.2-20-alpine3.19` | http://localhost:8081 | `admin` / `admin` |

All host ports and credentials can be overridden through env vars (see `.env.example`).
In pgAdmin, register the server with host `postgres`, port `5432`.

## Notes

- All data lives in named volumes (no host permission setup needed, including for Elasticsearch).
- On a Linux host, if Elasticsearch exits at startup: `sudo sysctl -w vm.max_map_count=262144`.
- Python client examples are in [`examples/`](examples/README.md).
- The `guest` RabbitMQ user is only allowed from localhost *inside* the container in the stock image; this
  compose file re-creates it with `RABBITMQ_DEFAULT_USER`, which lifts that restriction for dev use.

## Cleaning up Docker

- This stack only: `docker compose down -v --remove-orphans` (add `--rmi all` to remove the images too)
- Everything unused on the host (all projects, destructive): `docker system prune -a --volumes`
