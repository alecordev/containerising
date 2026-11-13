# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Static route, templated route (path param + fake data), CORS headers on the OPTIONS preflight."""
import re

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, run, step  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('MOCKOON_PORT', 3001)}"
    step("static route")
    expect("Hello from Mockoon" in http(f"{base}/hello").body, "/hello not served")
    step("templating: :id echoed, fake name generated")
    body = http(f"{base}/api/users/7").body
    expect('"id": 7' in body, f"id not echoed: {body[:200]}")
    expect(re.search(r'"name": "[A-Za-z]', body), f"no generated name: {body[:200]}")
    step("CORS preflight")
    r = http(f"{base}/hello", "OPTIONS",
             headers={"Origin": "http://example.test", "Access-Control-Request-Method": "GET"})
    expect(any(k.lower() == "access-control-allow-origin" for k in r.headers), f"no CORS headers: {dict(r.headers)}")


run(main)
