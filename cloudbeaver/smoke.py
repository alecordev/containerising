# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Landing page and GraphQL API both answer."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, run, step  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('CLOUDBEAVER_PORT', 8978)}"
    step("landing page")
    http(f"{base}/")
    step("GraphQL serverConfig")
    r = http(f"{base}/api/gql", "POST", json_body={"query": "query { serverConfig { name version } }"}).json()
    expect("serverConfig" in r.get("data", {}), f"unexpected GraphQL response: {r}")


run(main)
