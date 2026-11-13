# Redpanda

[Redpanda](https://www.redpanda.com/): a Kafka API-compatible streaming platform in a single C++ binary (no JVM, no ZooKeeper, built-in Schema Registry and HTTP Proxy). This template runs a single dev-container node plus **Redpanda Console** (web UI). Use it as a lighter drop-in for the [`kafka/`](../kafka) templates; any Kafka client works unchanged.

## Run

```bash
cd redpanda
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete the data volume
```

## Ports and URLs

| What | Address | Env override |
|---|---|---|
| Kafka API (host clients) | `localhost:19092` | `REDPANDA_KAFKA_PORT` |
| Kafka API (other containers on `redpanda-net`) | `redpanda:9092` | |
| Schema Registry | http://localhost:18081 | `REDPANDA_SCHEMA_REGISTRY_PORT` |
| HTTP Proxy (pandaproxy) | http://localhost:18082 | `REDPANDA_PROXY_PORT` |
| Admin API | http://localhost:9644 | `REDPANDA_ADMIN_PORT` |
| Console UI | http://localhost:8085 | `REDPANDA_CONSOLE_PORT` |

The host listener is on **19092** (not 9092) so it can run alongside the `kafka/` templates.

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `REDPANDA_VERSION` | `v26.2.6` | Broker image tag |
| `REDPANDA_CONSOLE_VERSION` | `v3.14.0` | Console image tag |
| `REDPANDA_MEMORY` | `1G` | Memory for the single shard |
| `REDPANDA_EXTERNAL_HOST` | `localhost` | Advertised host for host-side clients; set to your machine's name/IP for remote clients |

## Try it

```bash
docker compose exec redpanda rpk topic create demo -p 3
echo 'hello' | docker compose exec -T redpanda rpk topic produce demo
docker compose exec redpanda rpk topic consume demo -n 1 --offset start
docker compose exec redpanda rpk topic list
```

From the host with the Kafka CLI or a client library, use bootstrap server `localhost:19092`. Python:

```python
from confluent_kafka import Producer
p = Producer({"bootstrap.servers": "localhost:19092"})
p.produce("demo", b"hello"); p.flush()
```

HTTP Proxy: `curl localhost:18082/topics`.

## Notes

- `--mode=dev-container` disables hardware checks and fsync tuning: **not for production**.
- Containers on another compose network should join `redpanda-net` and use `redpanda:9092`.

## Resources

- https://docs.redpanda.com/
- https://docs.redpanda.com/current/get-started/quick-start/

## Smoke test

`python scripts/smoke.py redpanda` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run redpanda/smoke.py`); it needs only the Python standard library.
