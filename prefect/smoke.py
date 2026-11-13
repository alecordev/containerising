# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: the Prefect API reports healthy and the version endpoint answers."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('PREFECT_PORT', 4200)}/api"
    r = retry(lambda: http(f"{base}/health"), desc="Prefect /api/health")
    expect(r.body.strip() == "true", f"unexpected health body: {r.body!r}")
    expect(http(f"{base}/admin/version").json(), "no version returned")


run(main)
