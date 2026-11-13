# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: authenticated SET/GET round trip and confirm the server really is Valkey."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, run, sh  # noqa: E402

CLI = 'valkey-cli -a "$VALKEY_PASSWORD" --no-auth-warning '


def main() -> None:
    sh("valkey", CLI + "SET smoke hello")
    value = sh("valkey", CLI + "GET smoke").stdout.strip()
    expect(value == "hello", f"GET returned {value!r}")
    info = sh("valkey", CLI + "INFO server").stdout
    expect("valkey_version" in info, "INFO server has no valkey_version")
    sh("valkey", CLI + "DEL smoke")


run(main)
