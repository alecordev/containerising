# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: the Django admin login page is served by gunicorn."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run  # noqa: E402


def main() -> None:
    r = retry(lambda: http(f"http://localhost:{port('WEB_PORT', 8000)}/admin/login/"), desc="Django admin login")
    expect("Django" in r.body, "response does not look like Django admin")


run(main)
