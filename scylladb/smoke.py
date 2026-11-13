# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: create keyspace + table, insert and read a row with cqlsh."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, retry, run  # noqa: E402

# NetworkTopologyStrategy: Scylla creates keyspaces with tablets by default, which reject SimpleStrategy.
CQL = (
    "CREATE KEYSPACE IF NOT EXISTS smoke WITH replication={'class':'NetworkTopologyStrategy','replication_factor':1}; "
    "CREATE TABLE IF NOT EXISTS smoke.t(id int PRIMARY KEY, v text); "
    "INSERT INTO smoke.t(id,v) VALUES (1,'ok'); "
    "SELECT v FROM smoke.t WHERE id=1;"
)


def main() -> None:
    out = retry(lambda: exec_("scylla", "cqlsh", "-e", CQL).stdout, timeout=90, desc="cqlsh round trip")
    expect("ok" in out, f"unexpected cqlsh output: {out!r}")
    exec_("scylla", "cqlsh", "-e", "DROP KEYSPACE smoke;")


run(main)
