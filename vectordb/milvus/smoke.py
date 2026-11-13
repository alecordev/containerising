# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check (REST v2): create a collection, insert two vectors, search returns the closest."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402

API = f"http://localhost:{port('MILVUS_PORT', 19530)}/v2/vectordb"


def call(path: str, body: dict) -> dict:
    out = http(f"{API}/{path}", "POST", json_body=body).json()
    expect(out.get("code") == 0, f"{path} failed: {out}")
    return out


def main() -> None:
    http(f"http://localhost:{port('MILVUS_METRICS_PORT', 9091)}/healthz")
    http(f"{API}/collections/drop", "POST", json_body={"collectionName": "smoke"}, ok=range(200, 500))  # start clean
    try:
        call("collections/create", {"collectionName": "smoke", "dimension": 4})
        call("entities/insert", {"collectionName": "smoke", "data": [
            {"id": 1, "vector": [0.1, 0.2, 0.3, 0.4]}, {"id": 2, "vector": [0.9, 0.1, 0.1, 0.1]}]})

        def search() -> list | None:
            out = http(f"{API}/entities/search", "POST", json_body={
                "collectionName": "smoke", "data": [[0.1, 0.2, 0.3, 0.4]], "annsField": "vector", "limit": 1}).json()
            return out.get("data") if out.get("code") == 0 else None

        # The quick-setup collection auto-loads; retry briefly while it loads.
        rows = retry(search, timeout=60, desc="Milvus search")
        expect(rows[0]["id"] == 1, f"nearest neighbour should be id 1: {rows}")
    finally:
        http(f"{API}/collections/drop", "POST", json_body={"collectionName": "smoke"}, ok=range(200, 500))


run(main)
