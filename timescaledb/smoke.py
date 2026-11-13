# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: insert into the seeded hypertable, count rows, confirm TimescaleDB registered it."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, run, sh  # noqa: E402

PSQL = 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -tA -c '


def q(sql: str) -> str:
    return sh("timescaledb", PSQL + '"' + sql + '"').stdout.strip()


def main() -> None:
    q("INSERT INTO conditions VALUES (now(), 'sensor-2', 19.0)")
    count = q("SELECT count(*) FROM conditions")
    expect(count.isdigit() and int(count) >= 2, f"expected >= 2 rows (seed row + smoke row), got {count!r}")
    tables = q("SELECT hypertable_name FROM timescaledb_information.hypertables")
    expect("conditions" in tables.split(), f"'conditions' is not a hypertable: {tables!r}")


run(main)
