# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: connect to the FREEPDB1 pluggable database as the app user, insert a row, count rows."""
import re

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, run  # noqa: E402

CONNECT = 'sqlplus -s -L app/"$APP_USER_PASSWORD"@//localhost:1521/FREEPDB1'


def sqlplus(script: str) -> str:
    return exec_("oracle", "sh", "-c", CONNECT, input=script).stdout


def main() -> None:
    sqlplus("WHENEVER SQLERROR EXIT FAILURE\nINSERT INTO notes (body) VALUES ('smoke');\nCOMMIT;\nEXIT\n")
    out = sqlplus("SET HEADING OFF FEEDBACK OFF\nSELECT COUNT(*) FROM notes;\nEXIT\n")
    counts = [ln.strip() for ln in out.splitlines() if re.fullmatch(r"\s*\d+\s*", ln)]
    expect(counts and int(counts[0]) >= 2, f"expected >= 2 notes (seed row + smoke row), got {out!r}")


run(main)
