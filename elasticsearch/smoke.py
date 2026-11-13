# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: index a document, search it back, delete the index; Kibana answers."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    es = f"http://localhost:{port('ES_PORT', 9200)}"
    http(f"{es}/smoke/_doc/1?refresh=true", "PUT", json_body={"v": "ok"})
    hits = http(f"{es}/smoke/_search?q=v:ok").json()["hits"]["total"]["value"]
    expect(hits == 1, f"expected 1 hit, got {hits}")
    http(f"{es}/smoke", "DELETE")
    retry(lambda: http(f"http://localhost:{port('KIBANA_PORT', 5601)}/api/status"), timeout=90, desc="Kibana /api/status")


run(main)
