# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Static stub, response templating, body from __files, runtime stub via the admin API, unmatched -> 404."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, run, step  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('WIREMOCK_PORT', 8089)}"
    step("static stub")
    expect("Hello from WireMock" in http(f"{base}/hello").body, "/hello stub not served")
    step("response templating (path segment echoed)")
    expect('"id": 42' in http(f"{base}/api/users/42").body, "templated id missing")
    step("body from __files")
    expect("quarterly" in http(f"{base}/report").body, "__files body missing")
    step("register a stub at runtime through the admin API")
    http(f"{base}/__admin/mappings", "POST",
         json_body={"request": {"method": "GET", "url": "/runtime"}, "response": {"status": 201, "body": "created"}})
    expect(http(f"{base}/runtime", ok=(201,)).status == 201, "runtime stub not applied")
    step("unmatched request returns 404")
    http(f"{base}/does-not-exist", ok=(404,))


run(main)
