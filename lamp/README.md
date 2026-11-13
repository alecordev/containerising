# LAMP (PHP + Apache + MariaDB)

`php:8.4-apache` (with `mysqli` and `pdo_mysql` installed by the local `Dockerfile`) and `mariadb:11.8` (LTS).

```bash
docker compose up -d --build
```

Open http://localhost:8080 — `www/index.php` shows the PHP version and checks the database connection.
Put your own PHP files in `www/` (bind-mounted at `/var/www/html`).

## Configuration (env vars / optional `.env`, see `.env.example`)

| Variable | Default |
|---|---|
| `PHP_VERSION` | `8.4` |
| `MARIADB_VERSION` | `11.8` |
| `WEB_PORT` | `8080` |
| `MARIADB_ROOT_PASSWORD` | `root` |
| `MARIADB_DATABASE` | `testdb` |
| `MARIADB_USER` / `MARIADB_PASSWORD` | `username` / `password` |
| `TZ` | `UTC` |

The database is reachable from the PHP container as host `mariadb`. It is not published on the host;
add `ports: ["3306:3306"]` to the `mariadb` service if you need it. Data lives in the named volume `mariadb`.
