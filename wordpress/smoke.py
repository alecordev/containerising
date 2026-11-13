# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: MySQL is up and WordPress serves its install/home page (after redirects)."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, http, port, retry, run  # noqa: E402


def main() -> None:
    out = retry(lambda: exec_("db", "sh", "-c", 'mysql -h127.0.0.1 -uroot -p"$MYSQL_ROOT_PASSWORD" -N -e "select 1"').stdout,
                timeout=60, desc="mysql over TCP")
    expect(out.strip() == "1", f"unexpected mysql output: {out!r}")
    r = retry(lambda: http(f"http://localhost:{port('WORDPRESS_PORT', 8000)}/"), desc="WordPress")
    expect("wordpress" in r.body.lower(), "response does not look like WordPress")


run(main)
