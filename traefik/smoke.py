# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Routing by Host header through the entrypoint, dashboard API sees the router, unknown hosts 404."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run, step  # noqa: E402


def main() -> None:
    entry = f"http://localhost:{port('TRAEFIK_HTTP_PORT', 80)}/"
    step("whoami.localhost is routed to the demo service")
    retry(lambda: "Hostname:" in http(entry, headers={"Host": "whoami.localhost"}).body,
          timeout=30, interval=2, desc="route for whoami.localhost")

    step("dashboard API lists the router")
    routers = http(f"http://localhost:{port('TRAEFIK_DASHBOARD_PORT', 8088)}/api/http/routers").body
    expect("whoami" in routers, "router 'whoami' not found in the dashboard API")

    step("unknown host returns 404")
    r = http(entry, headers={"Host": "nope.localhost"}, ok=(404,))
    expect(r.status == 404, f"expected 404, got {r.status}")


run(main)
