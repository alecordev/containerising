# Kafka (KRaft, no ZooKeeper)

| Dir | What | Host ports |
|---|---|---|
| `simple/` | Single-node `apache/kafka:4.4.0` | 9092 |
| `advanced/docker-compose.yml` | Single node + Kafka UI (kafbat) | 9092, UI 8090 |
| `advanced/docker-compose_cluster.yml` | 3-node KRaft cluster + Kafka UI | 9092, 9094, 9096, UI 8090 |
| `advanced/docker-compose_settings.yml` | Single node with env-driven broker tuning (retention, partitions, heap, ...) | 9092 |
| `confluent/` | `cp-kafka` 8.3.3 (KRaft) + Schema Registry | 9092, 8081 |

The old Bitnami/ZooKeeper templates were removed (Bitnami images were retired and ZooKeeper mode no longer exists in Kafka 4).

## Run

```bash
cd simple            # or advanced / confluent
docker compose up -d
docker compose -f docker-compose_cluster.yml up -d   # advanced: cluster variant
docker compose down  # add -v to delete data
```

## Listeners

Each broker has two client listeners, so both containers and the host work:

- **Inside docker** (same compose network): `kafka:19092` (`confluent/`: `kafka:29092`)
- **From the host**: `localhost:9092` — the advertised address is `${KAFKA_EXTERNAL_HOST:-localhost}:${KAFKA_PORT:-9092}`. Set `KAFKA_EXTERNAL_HOST` to the machine's hostname/IP if clients run elsewhere.

## Environment

`KAFKA_VERSION` (4.4.0), `KAFKA_PORT` (9092), `KAFKA_EXTERNAL_HOST` (localhost), `CLUSTER_ID` (22-char base64 UUID, identical on all nodes), `KAFKA_UI_PORT` (8090), `CP_VERSION` (8.3.3), `SCHEMA_REGISTRY_PORT` (8081).

## Handy commands

```bash
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic demo --partitions 3 --replication-factor 1
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic demo
docker compose exec -it kafka /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic demo
docker compose exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic demo --from-beginning
docker compose exec kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
```

For `confluent/` the tools have no `.sh` suffix and no path: `docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list`.
Schema Registry: `curl http://localhost:8081/subjects`.

## Python example

`examples/producer_consumer.py` (run it with uv; dependencies come from the script header):

```bash
uv run examples/producer_consumer.py produce 10
uv run examples/producer_consumer.py consume
```

## Checks

Each compose file has a Python smoke test that creates a topic, produces and consumes a message (`confluent/` also registers a schema):
`simple/smoke.py`, `advanced/smoke.py`, `advanced/smoke.docker-compose_cluster.py`, `advanced/smoke.docker-compose_settings.py`, `confluent/smoke.py`.
Run one with `python scripts/smoke.py kafka/simple` (or `kafka/advanced/docker-compose_cluster.yml`); see `scripts/smokelib.py` for the helpers. With the stack already running, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run kafka/smoke.py`).

## Resources

- https://kafka.apache.org/documentation/
- https://hub.docker.com/r/apache/kafka
- https://docs.confluent.io/platform/current/installation/docker/config-reference.html
- https://github.com/kafbat/kafka-ui
