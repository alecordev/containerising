# Adminer

[Adminer](https://www.adminer.org/) is a single-file web UI for PostgreSQL, MySQL/MariaDB, SQLite, MS SQL, Oracle, MongoDB (plugin) and more. This template runs it on a shared Docker network (`dbnet`) so it can reach the database of **any other template** in this repo, without editing those stacks.

## Run

```bash
cd adminer
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
# optional throwaway Postgres to try it out
docker compose --profile demo up -d --wait
```

Open http://localhost:8082. Demo login: system `PostgreSQL`, server `demo-postgres`, user/password/database `demo`.

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `ADMINER_VERSION` | `6.3.0-standalone` | Image tag |
| `ADMINER_PORT` | `8082` | Host port (8080/8081 are used by many other templates) |
| `ADMINER_DEFAULT_SERVER` | `postgres` | Pre-filled server name |
| `ADMINER_DESIGN` | `pepa-linha` | UI theme |
| `DEMO_POSTGRES_VERSION` | `18.6-alpine` | Demo database tag |
| `DBNET_NAME` | `dbnet` | Name of the shared network |

## Reach another template's database

Adminer must share a Docker network with the database. Two ways:

**1. Attach a running container** (no file edits; lasts until the container is recreated):

```bash
docker network connect dbnet postgres            # container_name from postgresql/docker-compose.yml
docker network connect dbnet mongodb
```

Then log in with the container name as server (`postgres`, port 5432 default).

**2. Join the network from the other compose file** (permanent):

```yaml
services:
    postgresql:
        networks: [default, dbnet]

networks:
    dbnet:
        external: true
```

Start Adminer first (it creates `dbnet`). Hostnames are the service/container names; use the container port, not the host-mapped port.

## Notes

- Adminer has no authentication of its own beyond the database login: bind it to localhost only (`ADMINER_PORT` is published on all interfaces by default; use `127.0.0.1:8082:8080` in the compose file on shared machines).
- For a heavier multi-database client with saved connections, see [`cloudbeaver/`](../cloudbeaver).

## Resources

- https://hub.docker.com/_/adminer
- https://www.adminer.org/en/plugins/
