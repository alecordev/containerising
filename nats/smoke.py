# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: monitoring endpoints, then a JetStream round trip through the nats-box CLI (profile `tools`)."""
import json

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import dc, expect, http, port, run  # noqa: E402

MON = f"http://localhost:{port('NATS_MONITOR_PORT', 8222)}"


def nats(*args: str, check: bool = True) -> str:
    return dc("--profile", "tools", "run", "--rm", "-T", "nats-box", "nats", *args, check=check, timeout=120).stdout


def main() -> None:
    expect(http(f"{MON}/healthz").json().get("status") == "ok", "healthz is not ok")
    expect("config" in http(f"{MON}/jsz").json(), "JetStream (jsz) not enabled")
    nats("stream", "rm", "smoke", "--force", check=False)  # start clean (stream may not exist)
    try:
        nats("stream", "add", "smoke", "--subjects", "smoke.>", "--defaults")
        nats("pub", "smoke.hello", "hello nats")
        info = json.loads(nats("stream", "info", "smoke", "--json"))
        expect(info["state"]["messages"] == 1, f"expected 1 message in stream, got {info['state']}")
    finally:
        nats("stream", "rm", "smoke", "--force", check=False)


run(main)
