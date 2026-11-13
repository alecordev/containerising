# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: the Airflow API server reports a healthy metadata DB, scheduler, triggerer and dag processor."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    def healthy() -> dict:
        h = http(f"http://localhost:{port('AIRFLOW_PORT', 8080)}/api/v2/monitor/health").json()
        return h if all(h.get(k, {}).get("status") == "healthy" for k in ("metadatabase", "scheduler", "triggerer", "dag_processor")) else {}

    expect(retry(healthy, timeout=120, desc="metadatabase, scheduler, triggerer and dag_processor healthy"), "airflow not healthy")


run(main)
