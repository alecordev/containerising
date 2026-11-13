# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: create a temp table, insert, select (runs psql inside the container)."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, run  # noqa: E402

SQL = "create temp table smoke(i int); insert into smoke values (42); select i from smoke;"


def main() -> None:
    out = exec_("postgresql", "sh", "-c", 'psql -qtA -U "$POSTGRES_USER" -d "$POSTGRES_DB"', input=SQL).stdout
    expect(out.split()[-1] == "42", f"unexpected psql output: {out!r}")


run(main)
