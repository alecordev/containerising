# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: the standalone browser container reports a ready Grid."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    def ready() -> bool:
        return http(f"http://localhost:{port('GRID_PORT', 4444)}/status").json()["value"].get("ready") is True

    expect(retry(ready, timeout=120, desc="standalone Grid ready"), "grid not ready")


run(main)
