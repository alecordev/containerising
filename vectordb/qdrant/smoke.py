# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: create a collection, upsert two vectors, nearest-neighbour search returns the closest."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, expect, http, port, run  # noqa: E402

BASE = f"http://localhost:{port('QDRANT_HTTP_PORT', 6333)}"
KEY = env("QDRANT_API_KEY", "")
HEADERS = {"api-key": KEY} if KEY else {}


def main() -> None:
    http(f"{BASE}/readyz", headers=HEADERS)
    http(f"{BASE}/collections/smoke", "DELETE", headers=HEADERS, ok=range(200, 500))  # start clean
    try:
        r = http(f"{BASE}/collections/smoke", "PUT", headers=HEADERS,
                 json_body={"vectors": {"size": 4, "distance": "Cosine"}}).json()
        expect(r.get("result") is True, f"create collection failed: {r}")
        http(f"{BASE}/collections/smoke/points?wait=true", "PUT", headers=HEADERS, json_body={"points": [
            {"id": 1, "vector": [0.1, 0.2, 0.3, 0.4], "payload": {"name": "a"}},
            {"id": 2, "vector": [0.9, 0.1, 0.1, 0.1], "payload": {"name": "b"}},
        ]})
        res = http(f"{BASE}/collections/smoke/points/search", "POST", headers=HEADERS,
                   json_body={"vector": [0.1, 0.2, 0.3, 0.4], "limit": 1, "with_payload": True}).json()["result"]
        expect(res and res[0]["id"] == 1, f"nearest neighbour should be id 1: {res}")
    finally:
        http(f"{BASE}/collections/smoke", "DELETE", headers=HEADERS, ok=range(200, 500))


run(main)
