# MySQL

`mysql:8.4.13` (8.4 is the current LTS line). For a MariaDB equivalent see [`../mariadb`](../mariadb); WordPress and LAMP use their own embedded databases.

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
docker compose exec mysql mysql -uroot -p app          # prompts for the password (default: root)
mysql -h 127.0.0.1 -P 3306 -uapp -papp app      # from the host, if the client is installed
```

Connection string: `mysql://app:app@localhost:3306/app` (`mysql+pymysql://...` for SQLAlchemy).

## Environment variables

| Variable | Default |
|---|---|
| `MYSQL_VERSION` | `8.4.13` |
| `MYSQL_ROOT_PASSWORD` | `root` |
| `MYSQL_DATABASE` / `MYSQL_USER` / `MYSQL_PASSWORD` | `app` / `app` / `app` |
| `MYSQL_PORT` | `3306` |
| `TZ` | `UTC` |

Credentials and database are only applied on the first start of an empty volume (`docker compose down -v` to reset).

## Initialisation

Files in `./initdb/` (`*.sql`, `*.sql.gz`, `*.sh`) run once, alphabetically, on first start. The included `01-schema.sql` creates `app.notes` with one row.

## Notes

- Host port 3306 clashes with `wordpress/` and `mariadb/`; set `MYSQL_PORT` to run them together.
- Data lives in the named volume `mysql-data`.

## Resources

- https://hub.docker.com/_/mysql
- https://dev.mysql.com/doc/refman/8.4/en/

## Smoke test

`python scripts/smoke.py mysql` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run mysql/smoke.py`); it needs only the Python standard library.
