# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Push traces + logs + metrics through the Collector with telemetrygen, then read them back from
Tempo (traces), Loki (logs) and Prometheus (span metrics). Needs only docker + Python on the host."""
import subprocess
import urllib.parse

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, expect, http, port, retry, run, step  # noqa: E402

TELEMETRYGEN = "ghcr.io/open-telemetry/opentelemetry-collector-contrib/telemetrygen:v0.165.0"
NETWORK = "observability"  # fixed network name in docker-compose.yml
SERVICE = "smoke-svc"
LOG_LINE = "smoke log line"

TEMPO = f"http://localhost:{port('TEMPO_PORT', 3200)}"
LOKI = f"http://localhost:{port('LOKI_PORT', 3100)}"
PROM = f"http://localhost:{port('PROMETHEUS_PORT', 9090)}"
GRAFANA = f"http://localhost:{port('GRAFANA_PORT', 3000)}"


def telemetrygen(kind: str, *extra: str) -> None:
    cmd = ["docker", "run", "--rm", "--network", NETWORK, TELEMETRYGEN, kind,
           "--otlp-insecure", "--otlp-endpoint", "otel-collector:4317", "--service", SERVICE, *extra]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    expect(p.returncode == 0, f"telemetrygen {kind} failed:\n{p.stdout}\n{p.stderr}")


def query(base: str, path: str, **params: str) -> str:
    return http(f"{base}{path}?{urllib.parse.urlencode(params)}").body


def main() -> None:
    step("readiness endpoints")
    http(f"http://localhost:{port('OTELCOL_HEALTH_PORT', 13133)}/")
    http(f"{PROM}/-/ready")
    http(f"{LOKI}/ready")
    http(f"{TEMPO}/ready")
    http(f"{GRAFANA}/api/health")

    step("send traces, logs, metrics via OTLP")
    telemetrygen("traces", "--traces", "5")
    telemetrygen("logs", "--logs", "5", "--body", LOG_LINE)
    telemetrygen("metrics", "--metrics", "5")

    step("read back from Tempo, Loki and Prometheus")
    retry(lambda: '"traceID"' in query(TEMPO, "/api/search", tags=f"service.name={SERVICE}"),
          timeout=90, interval=3, desc=f"trace for {SERVICE} in Tempo")
    retry(lambda: LOG_LINE in query(LOKI, "/loki/api/v1/query_range", query=f'{{service_name="{SERVICE}"}}'),
          timeout=90, interval=3, desc=f"log line for {SERVICE} in Loki")
    retry(lambda: '"value"' in query(PROM, "/api/v1/query", query=f'traces_span_metrics_calls_total{{service_name="{SERVICE}"}}'),
          timeout=90, interval=3, desc=f"span metrics for {SERVICE} in Prometheus")

    step("provisioned Grafana datasources")
    ds = http(f"{GRAFANA}/api/datasources",
              auth=(env("GRAFANA_ADMIN_USER", "admin"), env("GRAFANA_ADMIN_PASSWORD", "admin"))).json()
    expect(any(d.get("uid") == "tempo" for d in ds), f"tempo datasource missing: {[d.get('uid') for d in ds]}")


run(main)
