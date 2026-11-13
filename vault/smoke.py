# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Write and read a KV v2 secret with the CLI inside the container, then read it over the HTTP API."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, http, port, run, step  # noqa: E402


def main() -> None:
    step("vault status")
    exec_("vault", "vault", "status")
    step("kv put / get via CLI")
    exec_("vault", "vault", "kv", "put", "-mount=secret", "smoke", "foo=bar")
    value = exec_("vault", "vault", "kv", "get", "-mount=secret", "-field=foo", "smoke").stdout.strip()
    expect(value == "bar", f"CLI read back {value!r}")
    step("read via HTTP API")
    r = http(f"http://localhost:{port('VAULT_PORT', 8200)}/v1/secret/data/smoke",
             headers={"X-Vault-Token": env("VAULT_DEV_ROOT_TOKEN", "root")}).json()
    expect(r["data"]["data"]["foo"] == "bar", f"API read back {r}")


run(main)
