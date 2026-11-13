# MariaDB

`mariadb:11.8.9` (11.8 is a long-term-support series). Drop-in alternative to [`../mysql`](../mysql).

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down      # add -v to delete data
```

## Access

| What | Value |
|---|---|
| Host / port | `localhost:3306` |
| Root login | `root` / `root` |
| App login | `app` / `app`, database `app` |

```bash
docker compose exec mariadb mariadb -uroot -p app      # prompts for the password (default: root)
```

Connection string: `mariadb://app:app@localhost:3306/app` (`mysql+pymysql://...` for SQLAlchemy).

## Environment variables

| Variable | Default |
|---|---|
| `MARIADB_VERSION` | `11.8.9` |
| `MARIADB_ROOT_PASSWORD` | `root` |
| `MARIADB_DATABASE` / `MARIADB_USER` / `MARIADB_PASSWORD` | `app` / `app` / `app` |
| `MARIADB_PORT` | `3306` |
| `TZ` | `UTC` |

Credentials and database are only applied on the first start of an empty volume. Files in `./initdb/` run once on first start (`01-schema.sql` creates `app.notes`).

## Notes

- Uses the official image's `healthcheck.sh` (`--connect --innodb_initialized`).
- Host port 3306 clashes with `mysql/` and `wordpress/`; override `MARIADB_PORT`.

## Resources

- https://hub.docker.com/_/mariadb
- https://mariadb.com/kb/en/

## Smoke test

`python scripts/smoke.py mariadb` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run mariadb/smoke.py`); it needs only the Python standard library.
