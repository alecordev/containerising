# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: authenticated SET/GET round trip, and unauthenticated access is refused."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, run  # noqa: E402


def main() -> None:
    pw = env("REDIS_PASSWORD", "password")
    cli = ["redis", "redis-cli", "-a", pw, "--no-auth-warning"]
    exec_(*cli, "set", "smoke", "ok")
    expect(exec_(*cli, "get", "smoke").stdout.strip() == "ok", "GET did not return the value that was SET")
    # REDISCLI_AUTH is set in the container (for the healthcheck), so clear it to test an anonymous client
    anon = exec_("redis", "sh", "-c", "unset REDISCLI_AUTH; redis-cli ping", check=False).stdout
    expect("NOAUTH" in anon or "Authentication" in anon, f"unauthenticated PING was not refused: {anon!r}")


run(main)
