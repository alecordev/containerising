# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: create a keyspace and table through cqlsh, write a row, read it back."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, retry, run  # noqa: E402


def cql(statement: str) -> str:
    return exec_("cassandra", "cqlsh", "-e", statement).stdout


def main() -> None:
    cql("CREATE KEYSPACE IF NOT EXISTS smoke WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}")
    cql("CREATE TABLE IF NOT EXISTS smoke.kv (k text PRIMARY KEY, v text)")
    cql("INSERT INTO smoke.kv (k, v) VALUES ('hello', 'world')")
    out = retry(lambda: "world" in cql("SELECT v FROM smoke.kv WHERE k = 'hello'"), timeout=30, desc="row to be readable")
    expect(out, "row not found")
    cql("DROP KEYSPACE smoke")


run(main)
