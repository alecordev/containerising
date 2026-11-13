# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: OrientDB Studio/REST answers on the first node."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    r = retry(lambda: http(f"http://localhost:{port('ORIENTDB_STUDIO_PORT', 2480)}/listDatabases"), desc="REST /listDatabases")
    expect("databases" in r.json(), f"unexpected response: {r.body[:200]}")


run(main)
