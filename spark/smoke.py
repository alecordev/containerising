# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: the Spark master UI reports both workers ALIVE."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    def alive() -> dict:
        d = http(f"http://localhost:{port('SPARK_MASTER_UI_PORT', 8080)}/json/").json()
        return d if d.get("aliveworkers") == 2 else {}

    d = retry(alive, timeout=90, desc="2 alive workers")
    expect(d.get("status") == "ALIVE", f"master status: {d.get('status')}")


run(main)
