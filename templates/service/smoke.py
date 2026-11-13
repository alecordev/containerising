# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check for this service: exercise it for real (write+read, query, API call); raise or sys.exit(1) on failure.

Two ways to run it (see scripts/README.md and scripts/smokelib.py):
  python scripts/smoke.py <dir>     start the stack, wait for healthchecks, run this file, tear the stack down
  python smoke.py  (or: uv run smoke.py)   run just this check against a stack you already started
  (in this directory; from elsewhere give the path: python <dir>/smoke.py)
"""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, http, port, run  # noqa: E402


def main() -> None:
    r = http(f"http://localhost:{port('MYSERVICE_PORT', 8080)}/")
    expect("nginx" in r.headers.get("Server", "").lower() or r.status == 200, "no response from myservice")
    expect("nginx version" in exec_("myservice", "nginx", "-v").stderr, "nginx -v failed")


run(main)
