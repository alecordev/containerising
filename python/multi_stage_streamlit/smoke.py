# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: the FastAPI API is healthy and the Streamlit dashboard reports ok."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    api = retry(lambda: http(f"http://localhost:{port('API_PORT', 8081)}/health"), desc="API /health")
    expect("ok" in api.body.lower(), f"api health: {api.body}")
    dash = retry(lambda: http(f"http://localhost:{port('DASHBOARD_PORT', 8501)}/_stcore/health"), desc="dashboard health")
    expect("ok" in dash.body.lower(), f"dashboard health: {dash.body}")


run(main)
