# Debezium (change data capture)

Streams row-level changes from PostgreSQL into Kafka topics.

```
PostgreSQL 18 (wal_level=logical) --pgoutput--> Debezium Connect 3.7 --> Kafka 4.4 (KRaft)
```

Self-contained: it ships its own single-node Kafka and Postgres, so it does not need the `../kafka` or `../postgresql` templates.

| Service | Image | Port |
|---|---|---|
| `postgres` | `postgres:18-alpine` (db `inventory`, table `customers`) | 5433 |
| `kafka` | `apache/kafka:4.4.0` | 9092 |
| `connect` | `quay.io/debezium/connect:3.7.1.Final` | 8083 |
| `register-connector` | one-shot, registers `connector-config.json` | - |
| `debezium-ui` | `quay.io/debezium/debezium-ui:2.5` (profile `ui`) | 8085 |

## Run

```bash
docker compose up -d --wait     # copy .env.example to .env first to override defaults (optional)
docker compose --profile ui up -d     # optional web UI at http://localhost:8085
docker compose down -v
```

Postgres is published on **5433** to avoid clashing with the other Postgres templates.

## See change events

```bash
# 1. connector status (expect RUNNING); the Connect image ships curl
docker compose exec connect curl -s http://localhost:8083/connectors/inventory-connector/status

# 2. change some data
docker compose exec postgres psql -U postgres -d inventory \
  -c "INSERT INTO customers (first_name, last_name, email) VALUES ('Ada', 'Lovelace', 'ada@example.com')" \
  -c "UPDATE customers SET last_name = 'King' WHERE first_name = 'Ada'" \
  -c "DELETE FROM customers WHERE first_name = 'Ada'"

# 3. read the events: op=r (snapshot), c (create), u (update), d (delete)
docker compose exec kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic dbserver1.public.customers --from-beginning
```

Topic names are `<topic.prefix>.<schema>.<table>` (`dbserver1.public.customers`).

## The connector

`connector-config.json` is registered automatically by `register-connector` (an idempotent `PUT`). To register another one by hand:

```bash
# the config file is mounted at /connector-config.json inside the connect container
docker compose exec connect curl -fsS -X PUT -H "Content-Type: application/json" --data @/connector-config.json http://localhost:8083/connectors/inventory-connector/config
docker compose exec connect curl -fsS -X DELETE http://localhost:8083/connectors/inventory-connector     # remove it
```

(The REST API is also published on the host at http://localhost:8083, so any HTTP client works.)

The database credentials and name inside `connector-config.json` match the defaults. If you override `POSTGRES_*`, edit the file too. The `init.sql` seed only runs on the first start of an empty volume.

## Environment

| Variable | Default |
|---|---|
| `DEBEZIUM_VERSION` / `DEBEZIUM_UI_VERSION` / `KAFKA_VERSION` | `3.7.1.Final` / `2.5` / `4.4.0` |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `postgres` / `postgres` / `inventory` |
| `PG_PORT` / `KAFKA_PORT` / `CONNECT_PORT` / `DEBEZIUM_UI_PORT` | `5433` / `9092` / `8083` / `8085` |
| `KAFKA_EXTERNAL_HOST` | `localhost` (set to your host name for remote clients) |

## Notes

- A replication slot (`debezium`) keeps WAL until it is consumed; `docker compose down -v` removes it with the volume.
- The Debezium UI is only published up to 2.5 and is optional; the REST API is the supported interface.
- Other sources (MySQL, MongoDB, SQL Server) work the same way: swap the database service and the connector class.

## Verify

`python ../scripts/smoke.py debezium` brings the stack up, runs `smoke.py` (waits for the connector, inserts a row and reads the change event back from Kafka) and tears it down. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run debezium/smoke.py`).

## Resources

- https://debezium.io/documentation/reference/stable/connectors/postgresql.html
