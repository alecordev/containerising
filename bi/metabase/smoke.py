# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Run the first-time setup through the API, log in, and list the bundled Sample Database."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, run  # noqa: E402

EMAIL = "smoke@example.com"
PASSWORD = "Containerising-123!"


def main() -> None:
    base = f"http://localhost:{port('METABASE_PORT', 3000)}"
    expect("ok" in http(f"{base}/api/health").body, "health is not ok")

    token = http(f"{base}/api/session/properties").json()["setup-token"]
    http(f"{base}/api/setup", "POST", json_body={
        "token": token,
        "user": {"first_name": "Smoke", "last_name": "Test", "email": EMAIL, "password": PASSWORD},
        "prefs": {"site_name": "Smoke", "site_locale": "en", "allow_tracking": False},
    })
    session = http(f"{base}/api/session", "POST", json_body={"username": EMAIL, "password": PASSWORD}).json()["id"]
    dbs = http(f"{base}/api/database", headers={"X-Metabase-Session": session}).body
    expect("sample database" in dbs.lower(), "Sample Database not listed")


run(main)
