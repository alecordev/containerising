# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: the Grid hub reports ready with the Chrome and Firefox nodes registered."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    def nodes() -> list:
        v = http(f"http://localhost:{port('GRID_PORT', 4444)}/status").json()["value"]
        return v["nodes"] if v.get("ready") and len(v.get("nodes", [])) >= 2 else []

    expect(retry(nodes, timeout=120, desc="Grid ready with >= 2 nodes"), "grid has no nodes")


run(main)
