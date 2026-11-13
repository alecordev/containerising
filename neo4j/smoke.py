# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: create a node and count it with cypher-shell inside the container."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, run  # noqa: E402

CYPHER = "CREATE (n:Smoke {v:1}) WITH n MATCH (m:Smoke) WITH count(m) AS c MATCH (d:Smoke) DELETE d RETURN c"


def main() -> None:
    out = exec_("neo4j", "sh", "-c", 'cypher-shell -u neo4j -p "${NEO4J_AUTH#neo4j/}" --format plain "$0"', CYPHER).stdout
    expect(int(out.split()[-1]) >= 1, f"unexpected cypher-shell output: {out!r}")


run(main)
