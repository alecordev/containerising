# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Health + version, create an admin with the CLI, create a repo through the API and read a file back."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import dc, expect, http, port, run, step  # noqa: E402

USER, PASSWORD = "smoke", "Smoke-Pass-123!"


def main() -> None:
    base = f"http://localhost:{port('GITEA_HTTP_PORT', 3001)}"
    step("health + version")
    expect("pass" in http(f"{base}/api/healthz").body.lower(), "healthz is not 'pass'")
    expect("version" in http(f"{base}/api/v1/version").json(), "no version in /api/v1/version")

    step("create admin via CLI")
    dc("exec", "-T", "-u", "git", "gitea", "gitea", "admin", "user", "create", "--admin",
       "--username", USER, "--password", PASSWORD, "--email", "smoke@example.com", "--must-change-password=false")

    step("create repo + read README back")
    repo = http(f"{base}/api/v1/user/repos", "POST", auth=(USER, PASSWORD),
                json_body={"name": "smoke-repo", "auto_init": True, "readme": "Default"}).json()
    expect(repo.get("full_name") == "smoke/smoke-repo", f"unexpected repo: {repo.get('full_name')}")
    readme = http(f"{base}/api/v1/repos/smoke/smoke-repo/contents/README.md", auth=(USER, PASSWORD)).json()
    expect(readme.get("name") == "README.md", f"README.md missing: {readme}")


run(main)
