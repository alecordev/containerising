# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: the PHP page is served and MariaDB accepts the root login."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, http, port, retry, run  # noqa: E402


def main() -> None:
    r = retry(lambda: http(f"http://localhost:{port('WEB_PORT', 8080)}/"), desc="Apache/PHP")
    expect(len(r.body) > 0, "empty response from php-apache")
    out = exec_("mariadb", "sh", "-c", 'mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" -N -e "select 1"').stdout
    expect(out.strip() == "1", f"unexpected mariadb output: {out!r}")


run(main)
