#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Show which host ports every template publishes, and which templates clash. Stdlib only; cross-OS.

Usage:
    python scripts/ports.py                 # clash report + full table
    python scripts/ports.py --clashes       # only host ports used by more than one template
    python scripts/ports.py --markdown      # table in Markdown (for docs)
    python scripts/ports.py --free 8000-8100   # unused host ports in a range, to pick a default for a new service

Ports are read from the compose files' ``"${VAR:-1234}:5678"`` and ``"1234:5678"`` mappings (compose
defaults); override with the variables at run time. Templates that clash are simply not meant to run
together on the same defaults.
"""
from __future__ import annotations

import argparse
import os
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__", ".docker", "templates"}
VAR = re.compile(r"""["']?\$\{(?P<var>\w+):-(?P<host>\d+)\}:(?P<ctr>\d+)(?:/\w+)?["']?""")
LIT = re.compile(r"""^\s*-\s*["']?(?:\d+\.\d+\.\d+\.\d+:)?(?P<host>\d+):(?P<ctr>\d+)(?:/\w+)?["']?\s*(?:#.*)?$""", re.M)


def is_compose(name: str) -> bool:
    return ".override." not in name and (name in ("compose.yml", "compose.yaml") or (name.startswith("docker-compose") and name.endswith((".yml", ".yaml"))))


def scan() -> dict[str, list[tuple[int, int, str]]]:
    """template (dir/file) -> [(host, container, variable)]"""
    out: dict[str, list[tuple[int, int, str]]] = {}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP)
        for f in sorted(filenames):
            if not is_compose(f):
                continue
            text = (Path(dirpath) / f).read_text(encoding="utf-8", errors="replace")
            key = (Path(dirpath) / f).relative_to(ROOT).as_posix()
            found = {(int(m["host"]), int(m["ctr"]), m["var"]) for m in VAR.finditer(text)}
            found |= {(int(m["host"]), int(m["ctr"]), "") for m in LIT.finditer(text)}
            if found:
                out[key] = sorted(found)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clashes", action="store_true")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--free", metavar="LOW-HIGH")
    a = ap.parse_args()
    ports = scan()
    by_port: dict[int, set[str]] = defaultdict(set)
    for key, items in ports.items():
        # variants of the same directory (kafka/advanced/*.yml) are alternatives, so group by directory
        d = key.rsplit("/", 1)[0] if "/" in key else key
        for host, _, _ in items:
            by_port[host].add(d)
    if a.free:
        low, high = (int(x) for x in a.free.split("-"))
        print(" ".join(str(p) for p in range(low, high + 1) if p not in by_port))
        return 0
    clashes = {p: sorted(ds) for p, ds in by_port.items() if len(ds) > 1}
    if a.markdown:
        print("| Host port | Used by |\n|---|---|")
        for p in sorted(by_port):
            print(f"| {p} | {', '.join(f'`{d}`' for d in sorted(by_port[p]))} |")
        return 0
    print("Host ports used by more than one template (override the port variable or run one at a time):")
    for p in sorted(clashes):
        print(f"  {p:>5}  {', '.join(clashes[p])}")
    if not a.clashes:
        print("\nAll published host ports (compose defaults):")
        for p in sorted(by_port):
            print(f"  {p:>5}  {', '.join(sorted(by_port[p]))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
