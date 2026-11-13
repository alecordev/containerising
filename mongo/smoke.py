# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: authenticated insert + count through mongosh, and Mongo Express answers."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, http, port, retry, run  # noqa: E402

JS = 'const c = db.getSiblingDB("smoke").t; c.insertOne({a: 1}); print("count=" + c.countDocuments()); c.drop();'


def main() -> None:
    out = exec_(
        "mongo", "mongosh", "--quiet", "-u", env("MONGO_USER", "admin"), "-p", env("MONGO_PASSWORD", "admin"),
        "--authenticationDatabase", "admin", "--eval", JS,
    ).stdout
    expect("count=1" in out, f"unexpected mongosh output: {out!r}")
    auth = (env("MONGO_EXPRESS_USER", "admin"), env("MONGO_EXPRESS_PASSWORD", "admin"))
    retry(lambda: http(f"http://localhost:{port('MONGO_EXPRESS_PORT', 8081)}/", auth=auth), desc="Mongo Express UI")


run(main)
