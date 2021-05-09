# PostgreSQL & PgAdmin

## Quick Start

- `cd compose-postgres`
- `docker-compose up -d`

## Environments

* `POSTGRES_USER` the default value is **postgres**
* `POSTGRES_PASSWORD` the default value is **postgres**
* `PGADMIN_PORT` the default value is **5050**
* `PGADMIN_DEFAULT_EMAIL` the default value is **pgadmin@pgadmin.org**
* `PGADMIN_DEFAULT_PASSWORD` the default value is **admin**

## Access to postgres

- `localhost:5432`
- **Username:** postgres (as a default)
- **Password:** postgres (as a default)

## Access to PgAdmin

- **URL:** `http://localhost:5050`
- **Username:** pgadmin@pgadmin.org (as a default)
- **Password:** admin (as a default)

## Add a new server in PgAdmin

- **Host name/address** `postgres`
- **Port** `5432`
- **Username** as `POSTGRES_USER`, by default: `postgres`
- **Password** as `POSTGRES_PASSWORD`, by default `postgres`
