# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: the vector extension works (create vector column, insert, distance query)."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, run  # noqa: E402

SQL = """
create temp table smoke_v(e vector(3));
insert into smoke_v values ('[1,2,3]');
select e <-> '[1,2,4]' from smoke_v;
"""


def main() -> None:
    out = exec_("postgresql-pgvector", "sh", "-c", 'psql -qtA -U "$POSTGRES_USER" -d "$POSTGRES_DB"', input=SQL).stdout
    expect(out.split()[-1] == "1", f"unexpected distance output: {out!r}")


run(main)
