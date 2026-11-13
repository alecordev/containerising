# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: UPSERT rows through the SQL shell, count them, and hit the readiness endpoint."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, http, port, retry, run  # noqa: E402


def sql(statement: str, *extra: str) -> str:
    return exec_("cockroach", "cockroach", "sql", "--insecure", "-d", "app", *extra, "-e", statement).stdout.strip()


def main() -> None:
    sql("CREATE TABLE IF NOT EXISTS smoke (id INT PRIMARY KEY, name STRING)")
    sql("UPSERT INTO smoke VALUES (1, 'hello'), (2, 'world')")
    lines = sql("SELECT count(*) FROM smoke", "--format=csv").splitlines()
    expect(lines and lines[-1].strip() == "2", f"expected count 2, got {lines!r}")
    retry(lambda: http(f"http://localhost:{port('COCKROACH_UI_PORT', 8080)}/health?ready=1").status == 200,
          timeout=30, desc="cockroach /health?ready=1")


run(main)
