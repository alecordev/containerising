# Oracle Database Free

Oracle Database Free (version 23.26, branded "Oracle AI Database 26ai Free", formerly 23ai) via the community-standard [`gvenzl/oracle-free`](https://hub.docker.com/r/gvenzl/oracle-free) image: tag `23.26.3-slim-faststart`.

- **slim**: trimmed image (no sample schemas, fewer options); **faststart**: database pre-created in the image, so start-up takes seconds.
- Oracle's own image (`container-registry.oracle.com/database/free`) is larger and takes minutes to initialise on first start; this template uses the gvenzl image for speed and convenience.

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait     # first start: image pull (~1.3 GB compressed) + ~1 minute
docker compose down             # add -v to delete data
```

> **Licence**: Oracle Database Free is free to use under the [Oracle Free Use Terms and Conditions](https://www.oracle.com/downloads/licenses/oracle-free-license.html). Limits: 2 CPU threads, 2 GB RAM and 12 GB of user data.

## Access

| What | Value |
|---|---|
| Listener | `localhost:1521` |
| Pluggable database (service name) | `FREEPDB1` |
| Admin | `system` / `oracle` (also `sys as sysdba`) |
| App user | `app` / `app` |

```bash
docker compose exec oracle sqlplus app@//localhost:1521/FREEPDB1   # prompts for the password (default: app)
docker compose exec oracle sqlplus / as sysdba
```

Connection strings: `app/app@//localhost:1521/FREEPDB1` (SQL*Plus/SQLcl), `jdbc:oracle:thin:@//localhost:1521/FREEPDB1`, Python `oracledb.connect(user="app", password="app", dsn="localhost:1521/FREEPDB1")` (`uv run --with oracledb python`; thin mode needs no client).

## Environment variables

| Variable | Default |
|---|---|
| `ORACLE_VERSION` | `23.26.3-slim-faststart` |
| `ORACLE_PASSWORD` | `oracle` (SYS / SYSTEM / PDBADMIN) |
| `APP_USER` / `APP_USER_PASSWORD` | `app` / `app` |
| `ORACLE_PORT` | `1521` |

The pluggable database is always `FREEPDB1` (service name `//localhost:1521/FREEPDB1`). Do not set `ORACLE_DATABASE` to that name: the image already ships it and would try to create it again (ORA-65012). Init scripts run as SYS in the CDB root, so `01-schema.sql` switches into `FREEPDB1` itself.

Passwords and the app user are only applied on the first start of an empty volume. Files in `./initdb/` (`*.sql`, `*.sh`) run once afterwards; `01-schema.sql` creates `app.notes`.

## Notes

- **Size and RAM**: the image is ~1.3 GB compressed (several GB on disk) and Oracle needs ~2 GB of RAM; give Docker Desktop at least 4 GB.
- **Architecture**: both amd64 and arm64 images exist.
- Data lives in the named volume `oracle-data`; `shm_size` is raised to 1 GB for the SGA.

## Resources

- https://github.com/gvenzl/oci-oracle-free
- https://www.oracle.com/database/free/

## Smoke test

`python scripts/smoke.py oracle-free` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run oracle-free/smoke.py`); it needs only the Python standard library.
