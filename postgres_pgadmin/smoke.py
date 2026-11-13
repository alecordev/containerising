# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: Postgres answers a query and pgAdmin's ping endpoint responds."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, http, port, retry, run  # noqa: E402


def main() -> None:
    out = exec_("postgres", "sh", "-c", 'psql -qtA -U "$POSTGRES_USER"', input="select 1;").stdout
    expect(out.strip() == "1", f"unexpected psql output: {out!r}")
    r = retry(lambda: http(f"http://localhost:{port('PGADMIN_PORT', 5050)}/misc/ping"), desc="pgAdmin /misc/ping")
    expect("PING" in r.body, f"unexpected ping body: {r.body!r}")


run(main)
