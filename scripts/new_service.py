#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Create a new service directory from ``templates/service``. Python 3.10+ stdlib only; cross-platform.

Usage:
    python scripts/new_service.py <name> [--docker]

    <name>     lowercase directory name, e.g. "redpanda" or "vectordb/qdrant" (last segment = service name)
    --docker   also keep Dockerfile + .dockerignore (from the *.example files)
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKEL = ROOT / "templates" / "service"
FILES = ("docker-compose.yml", ".env.example", "smoke.py", "README.md")
# The skeleton is a runnable stack named "myservice" (variables MYSERVICE_*); those words are the placeholders.


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    docker = "--docker" in argv
    if len(args) != 1:
        print(__doc__)
        return 2
    name = args[0].strip("/").replace("\\", "/")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_/-]*", name):
        print("name must match [a-z0-9][a-z0-9_/-]*", file=sys.stderr)
        return 2
    dest = ROOT / name
    if dest.exists():
        print(f"{dest} already exists", file=sys.stderr)
        return 1
    svc = name.rsplit("/", 1)[-1]
    upper = re.sub(r"[^A-Z0-9]", "_", svc.upper())
    dest.mkdir(parents=True)
    for f in FILES:
        text = (SKEL / f).read_text(encoding="utf-8")
        text = text.replace("MYSERVICE", upper).replace("myservice", svc)
        (dest / f).write_text(text, encoding="utf-8", newline="\n")
    if docker:
        shutil.copy(SKEL / "Dockerfile.example", dest / "Dockerfile")
        shutil.copy(SKEL / ".dockerignore.example", dest / ".dockerignore")
    print(f"Created {dest}")
    print(f"Next: edit docker-compose.yml, README.md and smoke.py, then run: python scripts/smoke.py {name}")
    print("      and add a row to the tables in AGENTS.md and README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
