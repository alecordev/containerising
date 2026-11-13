# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: create a collection, add a document, run a typo-tolerant search.

NOTE: the typesense-server binary segfaults on some hosts (seen on Windows 11 + Docker Desktop/WSL2),
see README.md. On such hosts this test fails because the container never becomes healthy.
"""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, expect, http, port, run  # noqa: E402

BASE = f"http://localhost:{port('TYPESENSE_PORT', 8108)}"
KEY = {"X-TYPESENSE-API-KEY": env("TYPESENSE_API_KEY", "dev-typesense-key")}


def main() -> None:
    expect(http(f"{BASE}/health").json().get("ok") is True, "Typesense /health is not ok")
    http(f"{BASE}/collections/smoke", "DELETE", headers=KEY, ok=range(200, 500))  # start clean
    try:
        http(f"{BASE}/collections", "POST", headers=KEY,
             json_body={"name": "smoke", "fields": [{"name": "title", "type": "string"}]})
        http(f"{BASE}/collections/smoke/documents", "POST", headers=KEY, json_body={"title": "hello typesense"})
        found = http(f"{BASE}/collections/smoke/documents/search?q=helo&query_by=title", headers=KEY).json()["found"]
        expect(found == 1, f"typo search 'helo' expected 1 hit, got {found}")
    finally:
        http(f"{BASE}/collections/smoke", "DELETE", headers=KEY, ok=range(200, 500))


run(main)
