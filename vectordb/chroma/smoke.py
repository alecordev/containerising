# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check (REST v2): create a collection, add two embeddings, query returns the closest."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, run  # noqa: E402

BASE = f"http://localhost:{port('CHROMA_PORT', 8000)}/api/v2"
DB = f"{BASE}/tenants/default_tenant/databases/default_database"


def main() -> None:
    expect("nanosecond heartbeat" in http(f"{BASE}/heartbeat").body, "unexpected heartbeat")
    http(f"{DB}/collections/smoke", "DELETE", ok=range(200, 500))  # start clean
    try:
        cid = http(f"{DB}/collections", "POST", json_body={"name": "smoke"}).json()["id"]
        expect(cid, "no collection id returned")
        http(f"{DB}/collections/{cid}/add", "POST", json_body={
            "ids": ["1", "2"],
            "embeddings": [[0.1, 0.2, 0.3, 0.4], [0.9, 0.1, 0.1, 0.1]],
            "documents": ["a", "b"],
        })
        ids = http(f"{DB}/collections/{cid}/query", "POST", json_body={
            "query_embeddings": [[0.1, 0.2, 0.3, 0.4]], "n_results": 1}).json()["ids"]
        expect(ids == [["1"]], f"nearest neighbour should be id 1: {ids}")
    finally:
        http(f"{DB}/collections/smoke", "DELETE", ok=range(200, 500))


run(main)
