# CloudBeaver

[CloudBeaver](https://dbeaver.com/docs/cloudbeaver/) is the web edition of DBeaver: a full-featured SQL client (data editor, ER diagrams, SQL autocomplete, export) for 100+ databases, with saved connections and multi-user support. A heavier alternative to [`adminer/`](../adminer) when you want persistent connection definitions.

## Run

```bash
cd cloudbeaver
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
```

Open http://localhost:8978 and sign in as `cbadmin` / `Admin12345` (change them in `.env` **before** the first start).

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `CLOUDBEAVER_VERSION` | `26.2.4` | Image tag |
| `CLOUDBEAVER_PORT` | `8978` | Host port |
| `CB_SERVER_NAME` | `CloudBeaver Dev` | Name shown in the UI |
| `CB_SERVER_URL` | `http://localhost:8978` | Public URL of the server |
| `CB_ADMIN_NAME` | `cbadmin` | Admin user created on first start |
| `CB_ADMIN_PASSWORD` | `Admin12345` | Admin password (8+ characters, with a digit) |
| `DBNET_NAME` | `dbnet` | Shared Docker network name |

The admin variables are only applied on the **first** start: afterwards credentials live in the `cloudbeaver-workspace` volume. To reset, `docker compose down -v`.

## Connect to the other templates

The container joins the shared `dbnet` network (the same one the `adminer/` template uses). Attach other stacks' containers to it and use the container name as the host:

```bash
docker network connect dbnet postgres      # postgresql/ template
docker network connect dbnet mongodb       # mongo/ template
```

In CloudBeaver: **New connection**, pick the driver, host = container name (`postgres`), port = container port (`5432`). To reach a service running on your host machine use `host.docker.internal`.

Drivers that are not bundled (e.g. Oracle, SQL Server variants) are downloaded on first use and cached in the workspace volume, so the container needs outbound network access the first time.

## Notes

- Connections you save live in the workspace volume, not in git. Back it up with `docker run --rm -v cloudbeaver_cloudbeaver-workspace:/w -v "$PWD":/b alpine tar czf /b/workspace.tgz -C /w .`.
- The default password is for local use only; do not expose port 8978 beyond localhost.

## Resources

- https://dbeaver.com/docs/cloudbeaver/Run-Docker-Container/
- https://github.com/dbeaver/cloudbeaver
