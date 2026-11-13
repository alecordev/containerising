# Observability (Grafana + Loki + Tempo + Prometheus + OpenTelemetry Collector)

A local LGTM-style stack. Applications send **OTLP** to one OpenTelemetry Collector, which fans out:

```
app / SDK ──OTLP──> otel-collector ──traces──> Tempo ──(span metrics)──> Prometheus
                         │                                  ▲
                         ├──logs (OTLP/HTTP)──> Loki        │
                         └──metrics (remote write)──────────┘      Grafana reads all three
```

| Service | Image | Host port |
|---|---|---|
| `otel-collector` | `otel/opentelemetry-collector-contrib:0.165.0` | `4317` (OTLP gRPC), `4318` (OTLP HTTP), `127.0.0.1:13133` (health) |
| `tempo` | `grafana/tempo:2.10.10` | `127.0.0.1:3200` |
| `loki` | `grafana/loki:3.7.9` | `127.0.0.1:3100` |
| `prometheus` | `prom/prometheus:v3.16.0` | `9090` |
| `grafana` | `grafana/grafana:13.2.6` | `3000` (`admin` / `admin`) |

`init` (chown the Loki/Tempo volumes) and `ready` (readiness gate) are one-shot helpers that exit after startup. Loki, Tempo and the Collector images are distroless (no shell/curl/wget), so they have no in-container healthcheck: `ready` polls Loki and Tempo from a busybox container, and the Collector exposes its `health_check` extension on `13133`.

> **Port clash with the `grafana/` template** (Grafana `3000`, Prometheus `9090`): run only one at a time, or override `GRAFANA_PORT` / `PROMETHEUS_PORT` (also `dagster/` and `gitea/` use 3000-range ports; see their READMEs).

## Run

```bash
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
docker compose down    # add -v to delete all telemetry data
```

Open Grafana at http://localhost:3000 → **Explore**. Datasources are provisioned (`grafana/provisioning/datasources/datasources.yaml`) and correlated:

- Prometheus exemplars → Tempo
- Loki `trace_id` → Tempo (a derived-field link on log lines)
- Tempo spans → the matching Loki logs and Prometheus metrics, service graph (from span metrics)

## Send test telemetry

With `telemetrygen` on the compose network (no install needed):

```bash
TG=ghcr.io/open-telemetry/opentelemetry-collector-contrib/telemetrygen:v0.165.0
docker run --rm --network observability $TG traces  --otlp-insecure --otlp-endpoint otel-collector:4317 --service demo --traces 20
docker run --rm --network observability $TG logs    --otlp-insecure --otlp-endpoint otel-collector:4317 --service demo --logs 20 --body "hello"
docker run --rm --network observability $TG metrics --otlp-insecure --otlp-endpoint otel-collector:4317 --service demo --metrics 20
```

Or OTLP/HTTP from the host with plain Python (a log record, then query it back from Loki, Tempo and Prometheus):

```python
import json, time, urllib.parse, urllib.request


def call(url, body=None):
    req = urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req).read().decode()


call("http://localhost:4318/v1/logs", {"resourceLogs": [{
    "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "py-demo"}}]},
    "scopeLogs": [{"logRecords": [{"timeUnixNano": str(time.time_ns()), "severityText": "INFO",
                                   "body": {"stringValue": "hello from python"}}]}]}]})
time.sleep(3)
q = urllib.parse.urlencode({"query": '{service_name="py-demo"}'})
print(call(f"http://localhost:3100/loki/api/v1/query_range?{q}"))
print(call("http://localhost:3200/api/search?tags=service.name%3Ddemo"))
q = urllib.parse.urlencode({"query": 'traces_span_metrics_calls_total{service_name="demo"}'})
print(call(f"http://localhost:9090/api/v1/query?{q}"))
```

## Instrument an application

Point any OpenTelemetry SDK at the Collector:

Set these environment variables for the application:

- `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` (or `http://otel-collector:4317` inside the compose network)
- `OTEL_SERVICE_NAME=my-service`

For containers, attach them to the `observability` network (`networks: { observability: { external: true } }`).

## Configuration files

| File | Purpose |
|---|---|
| `otel-collector/otel-collector.yaml` | receivers (OTLP), `spanmetrics` connector, exporters to Tempo/Loki/Prometheus |
| `loki/loki.yaml` | single binary, filesystem, TSDB v13, structured metadata (needed for OTLP) |
| `tempo/tempo.yaml` | single binary, local storage, 24 h block retention |
| `prometheus/prometheus.yml` | self/stack scrape jobs; remote-write receiver enabled by a flag in compose |
| `grafana/provisioning/datasources/datasources.yaml` | datasources and correlations |

Grafana Alloy (the Collector distribution from Grafana) is a drop-in alternative to `otel-collector` if you prefer it; not included.

## Environment

See `.env.example`: image versions, host ports (`GRAFANA_PORT`, `PROMETHEUS_PORT`, `LOKI_PORT`, `TEMPO_PORT`, `OTLP_GRPC_PORT`, `OTLP_HTTP_PORT`, `OTELCOL_HEALTH_PORT`), `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD`, `PROMETHEUS_RETENTION` (`7d`).

## Resources

- https://grafana.com/docs/loki/latest/send-data/otel/
- https://grafana.com/docs/tempo/latest/
- https://opentelemetry.io/docs/collector/
- https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/cmd/telemetrygen
