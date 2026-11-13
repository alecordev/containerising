# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: create a class (no vectorizer), insert an object with a vector, nearVector GraphQL query."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402

BASE = f"http://localhost:{port('WEAVIATE_HTTP_PORT', 8080)}"
QUERY = "{ Get { Smoke(nearVector:{vector:[0.1,0.2,0.3,0.4]}, limit:1){ name } } }"


def main() -> None:
    http(f"{BASE}/v1/.well-known/ready")
    http(f"{BASE}/v1/schema/Smoke", "DELETE", ok=range(200, 500))  # start clean
    try:
        http(f"{BASE}/v1/schema", "POST", json_body={
            "class": "Smoke", "vectorizer": "none", "properties": [{"name": "name", "dataType": ["text"]}]})
        http(f"{BASE}/v1/objects", "POST", json_body={
            "class": "Smoke", "properties": {"name": "a"}, "vector": [0.1, 0.2, 0.3, 0.4]})

        def nearest() -> str | None:
            rows = http(f"{BASE}/v1/graphql", "POST", json_body={"query": QUERY}).json()["data"]["Get"]["Smoke"]
            return rows[0]["name"] if rows else None

        name = retry(nearest, timeout=30, desc="nearVector result")
        expect(name == "a", f"expected object 'a', got {name!r}")
    finally:
        http(f"{BASE}/v1/schema/Smoke", "DELETE", ok=range(200, 500))


run(main)
