# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: cluster health, produce+consume through rpk, then Schema Registry and Console."""
import re

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import SmokeError, exec_, expect, http, port, retry, run  # noqa: E402


def rpk(*args: str, input: str | None = None, check: bool = True) -> str:
    return exec_("redpanda", "rpk", *args, input=input, check=check).stdout


def reachable(url: str) -> bool:
    try:
        return http(url, ok=range(200, 400)).status < 400
    except SmokeError:
        return False


def main() -> None:
    health = rpk("cluster", "health")
    expect(re.search(r"Healthy:\s+true", health), f"cluster not healthy:\n{health}")
    rpk("topic", "delete", "smoke", check=False)  # start clean
    try:
        rpk("topic", "create", "smoke", "-p", "1")
        rpk("topic", "produce", "smoke", input="hello redpanda\n")
        out = rpk("topic", "consume", "smoke", "-n", "1", "--offset", "start")
        expect("hello redpanda" in out, f"consumed message not found:\n{out}")
    finally:
        rpk("topic", "delete", "smoke", check=False)
    http(f"http://localhost:{port('REDPANDA_SCHEMA_REGISTRY_PORT', 18081)}/subjects")
    console = f"http://localhost:{port('REDPANDA_CONSOLE_PORT', 8085)}"
    # /admin/health exists in recent Console versions; fall back to the UI root.
    retry(lambda: reachable(f"{console}/admin/health") or reachable(f"{console}/"), timeout=30, desc="Redpanda Console")


run(main)
