# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: add documents, wait for the async indexing queue, run a typo-tolerant search."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, expect, http, port, retry, run  # noqa: E402

BASE = f"http://localhost:{port('MEILI_PORT', 7700)}"
AUTH = {"Authorization": "Bearer " + env("MEILI_MASTER_KEY", "dev-master-key-change-me-16b")}


def main() -> None:
    expect(http(f"{BASE}/health").json().get("status") == "available", "Meilisearch not available")
    try:
        http(f"{BASE}/indexes/smoke/documents", "POST", headers=AUTH,
             json_body=[{"id": 1, "title": "Carol"}, {"id": 2, "title": "Wonder Woman"}])
        # Indexing is asynchronous: wait for the task queue to drain.
        retry(lambda: http(f"{BASE}/tasks?statuses=enqueued,processing", headers=AUTH).json()["results"] == [],
              timeout=60, interval=1, desc="Meilisearch task queue to drain")
        hits = http(f"{BASE}/indexes/smoke/search", "POST", headers=AUTH, json_body={"q": "carrol"}).json()["hits"]
        expect(any(h["title"] == "Carol" for h in hits), f"typo search 'carrol' did not find Carol: {hits}")
    finally:
        http(f"{BASE}/indexes/smoke", "DELETE", headers=AUTH, ok=range(200, 500))


run(main)
