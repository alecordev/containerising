# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Check /health, log in through the REST API as the bootstrapped admin, and confirm the metadata DB is Postgres."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, http, port, run  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('SUPERSET_PORT', 8088)}"
    user, password = env("SUPERSET_ADMIN_USER", "admin"), env("SUPERSET_ADMIN_PASSWORD", "admin")

    expect(http(f"{base}/health").body.strip() == "OK", "/health did not return OK")

    token = http(f"{base}/api/v1/security/login", "POST",
                 json_body={"username": user, "password": password, "provider": "db", "refresh": True}).json()["access_token"]
    me = http(f"{base}/api/v1/me/", headers={"Authorization": f"Bearer {token}"}).json()
    expect(me["result"]["username"] == user, f"unexpected /me result: {me}")

    users = exec_("postgres", "sh", "-c", 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "select count(*) from ab_user"').stdout
    expect(int(users.strip()) >= 1, "no users in the Postgres metadata database")


run(main)
