# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: Grafana, Prometheus, InfluxDB and Alertmanager are all ready."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    g = retry(lambda: http(f"http://localhost:{port('GRAFANA_PORT', 3000)}/api/health"), desc="Grafana")
    expect(g.json().get("database") == "ok", f"grafana: {g.body}")
    retry(lambda: http(f"http://localhost:{port('PROMETHEUS_PORT', 9090)}/-/ready"), desc="Prometheus")
    i = retry(lambda: http(f"http://localhost:{port('INFLUXDB_PORT', 8086)}/health"), desc="InfluxDB")
    expect(i.json().get("status") == "pass", f"influxdb: {i.body}")
    retry(lambda: http(f"http://localhost:{port('ALERTMANAGER_PORT', 9093)}/-/ready"), desc="Alertmanager")


run(main)
