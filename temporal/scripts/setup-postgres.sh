#!/bin/sh
# Create the Temporal databases and apply schemas (idempotent). Runs in the admin-tools image.
# Shell on purpose: it runs inside the temporalio/admin-tools image, which ships no Python.
set -eu

: "${POSTGRES_SEEDS:?POSTGRES_SEEDS is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
# The password is read by temporal-sql-tool from SQL_PASSWORD.
PORT="${DB_PORT:-5432}"
SQL="temporal-sql-tool --plugin postgres12 --ep ${POSTGRES_SEEDS} -u ${POSTGRES_USER} -p ${PORT}"
SCHEMA=/etc/temporal/schema/postgresql/v12

echo "Waiting for PostgreSQL at ${POSTGRES_SEEDS}:${PORT}..."
nc -z -w 10 "${POSTGRES_SEEDS}" "${PORT}"

for db in temporal visibility; do
    name=temporal
    [ "$db" = visibility ] && name=temporal_visibility
    echo "Setting up database ${name}..."
    ${SQL} --db "${name}" create
    ${SQL} --db "${name}" setup-schema -v 0.0
    ${SQL} --db "${name}" update-schema -d "${SCHEMA}/${db}/versioned"
done

echo "PostgreSQL schema setup complete"
