# WordPress

`wordpress:php8.4-apache` + `mysql:8.4` (LTS).

```bash
docker compose up -d
```

Open http://localhost:8000 and complete the installer.

| Variable | Default |
|---|---|
| `WORDPRESS_PORT` | `8000` |
| `MYSQL_PORT` | `3306` |
| `MYSQL_ROOT_PASSWORD` | `root` |
| `WORDPRESS_DB_NAME` / `WORDPRESS_DB_USER` / `WORDPRESS_DB_PASSWORD` | `wordpress` / `wordpress` / `wordpress` |

Data lives in the named volumes `db_data` (database) and `wp_html` (WordPress files, plugins, uploads).
To edit themes/plugins from the host, replace `wp_html` by a bind mount such as `./.docker/wp_html:/var/www/html`.
Reset everything with `docker compose down -v`.
