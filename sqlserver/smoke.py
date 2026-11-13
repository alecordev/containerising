# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: create a database and table with sqlcmd, insert rows, count them."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, run, sh  # noqa: E402

# sqlcmd is not on PATH in the mssql image; -C trusts the container's self-signed certificate.
SQLCMD = '/opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -b -P "$MSSQL_SA_PASSWORD" '


def main() -> None:
    sh("sqlserver", SQLCMD + '''-Q "IF DB_ID('smoke') IS NULL CREATE DATABASE smoke" ''')
    sh("sqlserver", SQLCMD + '''-d smoke -Q "IF OBJECT_ID('t') IS NOT NULL DROP TABLE t; CREATE TABLE t (id INT, name NVARCHAR(50)); INSERT INTO t VALUES (1, 'hello'), (2, 'world');" ''')
    out = sh("sqlserver", SQLCMD + '''-d smoke -h -1 -W -Q "SET NOCOUNT ON; SELECT COUNT(*) FROM t" ''').stdout
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    expect(lines and lines[0] == "2", f"expected count 2, got {lines!r}")


run(main)
