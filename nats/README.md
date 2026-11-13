# NATS

[NATS](https://nats.io/): lightweight, high-performance messaging (pub/sub, request/reply, queue groups) with **JetStream** for persistence, streams and consumers. A much smaller alternative to Kafka/RabbitMQ for service messaging. This template runs a single server with JetStream enabled and the HTTP monitoring port open.

## Run

```bash
cd nats
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete the JetStream data volume
```

## Ports and URLs

| What | Address | Env override |
|---|---|---|
| Client connections | `nats://localhost:4222` | `NATS_PORT` |
| Monitoring | http://localhost:8222 (`/healthz`, `/varz`, `/jsz`, `/connz`) | `NATS_MONITOR_PORT` |

No authentication is configured (local development only).

## Environment variables

| Variable | Default | Notes |
|---|---|---|
| `NATS_VERSION` | `2.15.3-alpine` | Server image tag |
| `NATS_BOX_VERSION` | `0.20.2` | CLI toolbox image tag |

## Try it with the CLI (nats-box, profile `tools`)

The `nats-box` service is only started on demand and is preconfigured with `NATS_URL=nats://nats:4222`:

Every command is `docker compose --profile tools run --rm nats-box nats <args>` (shown here as `nats <args>`; wrap it in a shell alias or function if you like, the syntax differs per shell):

```text
nats stream add orders --subjects "orders.>" --defaults
nats pub orders.new '{"id":1}'
nats stream info orders
nats consumer add orders worker --pull --defaults
nats consumer next orders worker --count 1
nats stream rm orders --force
```

For example: `docker compose --profile tools run --rm nats-box nats stream info orders`. For an interactive shell inside the toolbox: `docker compose --profile tools run --rm nats-box sh`.

Plain pub/sub in two terminals: `nats sub 'greet.*'` and `nats pub greet.world hi`.

Python (`uv run --with nats-py python`): `await nats.connect("nats://localhost:4222")`.

## Notes

- The server image is `scratch`-based on other tags; the `-alpine` tag is used here so a shell-based healthcheck is possible.
- JetStream data lives in the `nats-data` volume (`-sd /data`).

## Resources

- https://docs.nats.io/
- https://docs.nats.io/nats-concepts/jetstream
- https://github.com/nats-io/nats.docker

## Smoke test

`python scripts/smoke.py nats` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run nats/smoke.py`); it needs only the Python standard library.
