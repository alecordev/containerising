# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: write+read as root, then log in as the application user."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, run, sh  # noqa: E402


def main() -> None:
    sh("mariadb", """mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" app -e "INSERT INTO notes (body) VALUES ('smoke')" """)
    out = sh("mariadb", """mariadb -N -uroot -p"$MARIADB_ROOT_PASSWORD" app -e "SELECT COUNT(*) FROM notes" """).stdout.strip()
    expect(out.isdigit() and int(out) >= 2, f"expected >= 2 notes (seed row + smoke row), got {out!r}")
    out = sh("mariadb", """mariadb -N -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" "$MARIADB_DATABASE" -e "SELECT 1" """).stdout.strip()
    expect(out == "1", f"app user login failed: {out!r}")


run(main)
