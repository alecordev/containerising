# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Liveness, readiness (includes the DB connection), the public settings endpoint and the CLI version."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, http, port, run, step  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('N8N_PORT', 5678)}"
    step("healthz + readiness")
    expect("ok" in http(f"{base}/healthz").body, "healthz is not ok")
    expect("ok" in http(f"{base}/healthz/readiness").body, "readiness is not ok")
    step("public settings")
    expect("data" in http(f"{base}/rest/settings").json(), "settings payload has no 'data'")
    step("CLI version")
    version = exec_("n8n", "n8n", "--version").stdout.strip()
    expect(version == env("N8N_VERSION", "2.48.2"), f"unexpected n8n version {version!r}")


run(main)
