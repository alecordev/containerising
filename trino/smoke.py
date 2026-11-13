# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Query the tpch benchmark catalog, then round-trip a table through the memory catalog."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, run  # noqa: E402


def trino(sql: str) -> str:
    return exec_("trino", "trino", "--execute", sql).stdout


def main() -> None:
    expect('"25"' in trino("SELECT count(*) FROM tpch.tiny.nation"), "tpch.tiny.nation should have 25 rows")
    trino("CREATE TABLE memory.default.smoke AS SELECT nationkey, name FROM tpch.tiny.nation WHERE regionkey = 1")
    expect('"5"' in trino("SELECT count(*) FROM memory.default.smoke"), "memory.default.smoke should have 5 rows")


run(main)
