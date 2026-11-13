# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: create an index, index a document, search it, delete the index, ping Dashboards."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402

BASE = f"http://localhost:{port('OPENSEARCH_PORT', 9200)}"


def main() -> None:
    http(f"{BASE}/smoke", "DELETE", ok=range(200, 500))  # start clean
    try:
        http(f"{BASE}/smoke", "PUT", json_body={})
        http(f"{BASE}/smoke/_doc/1?refresh=true", "POST", json_body={"title": "hello opensearch"})
        hits = http(f"{BASE}/smoke/_search?q=title:hello").json()["hits"]["total"]["value"]
        expect(hits == 1, f"expected 1 hit, got {hits}")
    finally:
        http(f"{BASE}/smoke", "DELETE", ok=range(200, 500))
    retry(lambda: http(f"http://localhost:{port('DASHBOARDS_PORT', 5602)}/api/status").status == 200,
          timeout=60, desc="OpenSearch Dashboards /api/status")


run(main)
