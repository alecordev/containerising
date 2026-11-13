#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Bring each compose stack up, wait for healthchecks, run its smoke test, tear it down.

Python 3.10+ standard library only; works on Linux, macOS and Windows (no bash needed).

Usage:
    python scripts/smoke.py [options] [target ...]

Targets (default: every compose file in the repo, except dirs containing a ``.smoke-skip`` file):
    postgresql                                  a directory (its docker-compose.yml)
    kafka/advanced                              a directory
    kafka/advanced/docker-compose_cluster.yml   one specific compose file

Options:
    -l, --list            list targets and exit
    -k, --keep            leave the stack running afterwards (only sensible with one target)
    -r, --rmi             remove images after teardown (``down --rmi all``) to save disk
    -w, --wait SECONDS    ``--wait-timeout`` for ``up`` (default 300)
    -p, --project NAME    compose project name (default "smoke"; only this project is ever touched)
    -x, --exclude PATTERN skip targets whose path contains PATTERN (repeatable)
        --report FILE     write a JSON summary of the run

Smoke tests: ``<dir>/smoke.py`` for docker-compose.yml/compose.yml, or ``<dir>/smoke.<compose-stem>.py``
for other compose files. They run in the service directory with ``scripts/`` on PYTHONPATH and the
project-scoped compose command in ``SMOKE_DC`` (JSON); see ``scripts/smokelib.py``. Without a smoke test
the stack is only checked for becoming healthy.

Logs: $SMOKE_LOG_DIR or <tmp>/smoke-logs/<target>.log. Exit code is non-zero if any target failed.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPOSE_NAMES = ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".docker"}
MAX_DEPTH = 4


def is_compose_file(name: str) -> bool:
    if ".override." in name:
        return False
    return name in COMPOSE_NAMES or (name.startswith("docker-compose") and name.endswith((".yml", ".yaml")))


def discover() -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = Path(dirpath).relative_to(ROOT)
        if len(rel.parts) >= MAX_DEPTH:
            dirnames[:] = []
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        if ".smoke-skip" in filenames:
            continue
        for fn in sorted(filenames):
            if is_compose_file(fn):
                found.append((rel / fn))
    return sorted(found, key=lambda p: p.as_posix())


def resolve(target: str) -> Path:
    t = Path(target.replace("\\", "/").rstrip("/"))
    p = ROOT / t
    if p.is_file():
        return t
    if p.is_dir():
        for name in COMPOSE_NAMES:
            if (p / name).is_file():
                return t / name
        raise SystemExit(f"no compose file in {target}")
    raise SystemExit(f"unknown target {target}")


def smoke_file_for(compose: Path) -> Path:
    d = ROOT / compose.parent
    if compose.name in ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"):
        return d / "smoke.py"
    return d / f"smoke.{compose.stem}.py"


class Result:
    def __init__(self, target: str, ok: bool, seconds: float, log: Path, note: str = "") -> None:
        self.target, self.ok, self.seconds, self.log, self.note = target, ok, seconds, log, note


def run_target(compose: Path, args: argparse.Namespace, logdir: Path) -> Result:
    d = ROOT / compose.parent
    target = compose.as_posix()
    log = logdir / (target.replace("/", "_") + ".log")
    env_args: list[str] = []
    if not (d / ".env").exists() and (d / ".env.example").exists():
        env_args = ["--env-file", ".env.example"]
    dc = ["docker", "compose", "-p", args.project, *env_args, "-f", compose.name]
    print(f"=== {target}", flush=True)
    start = time.monotonic()
    rc = 0
    note = ""
    with open(log, "w", encoding="utf-8", errors="replace") as lf:
        def run(cmd: list[str], timeout: float, extra_env: dict[str, str] | None = None) -> int:
            lf.write("+ " + " ".join(cmd) + "\n")
            lf.flush()
            e = os.environ.copy()
            e.update(extra_env or {})
            try:
                return subprocess.run(cmd, cwd=d, stdout=lf, stderr=subprocess.STDOUT, timeout=timeout, env=e).returncode
            except subprocess.TimeoutExpired:
                lf.write(f"!! timed out after {timeout}s\n")
                return 124

        try:
            rc = run([*dc, "up", "-d", "--build", "--wait", "--wait-timeout", str(args.wait)], args.wait + 600)
            run([*dc, "ps", "-a", "--format", "{{.Service}} {{.State}} {{.Health}}"], 60)
            if rc != 0:
                note = "stack did not become healthy"
                run([*dc, "logs", "--tail", "40"], 120)
            else:
                sf = smoke_file_for(compose)
                if sf.exists():
                    pp = os.pathsep.join(filter(None, [str(ROOT / "scripts"), os.environ.get("PYTHONPATH", "")]))
                    rc = run([sys.executable, str(sf)], 600, {"SMOKE_DC": json.dumps(dc), "PYTHONPATH": pp, "PYTHONUTF8": "1"})
                    if rc != 0:
                        note = f"{sf.name} failed"
                else:
                    lf.write(f"(no {sf.name}: only checked that the stack becomes healthy)\n")
                    note = "healthy only (no smoke test)"
        finally:
            if not args.keep:
                down = [*dc, "down", "-v", "--remove-orphans"] + (["--rmi", "all"] if args.rmi else [])
                run(down, 600)
    secs = time.monotonic() - start
    res = Result(target, rc == 0, secs, log, note)
    if res.ok:
        print(f"PASS {target} ({secs:.0f}s){' - ' + note if note else ''}", flush=True)
    else:
        print(f"FAIL {target} (rc={rc}, {secs:.0f}s) {note}\n  log: {log}")
        try:
            tail = log.read_text(encoding="utf-8", errors="replace").splitlines()[-25:]
            print("\n".join("  | " + ln[:240] for ln in tail), flush=True)
        except OSError:
            pass
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="*")
    ap.add_argument("-l", "--list", action="store_true")
    ap.add_argument("-k", "--keep", action="store_true")
    ap.add_argument("-r", "--rmi", action="store_true")
    ap.add_argument("-w", "--wait", type=int, default=300)
    ap.add_argument("-p", "--project", default="smoke")
    ap.add_argument("-x", "--exclude", action="append", default=[])
    ap.add_argument("--report")
    args = ap.parse_args()

    targets = [resolve(t) for t in args.targets] if args.targets else discover()
    targets = [t for t in targets if not any(x in t.as_posix() for x in args.exclude)]
    if args.list:
        print("\n".join(t.as_posix() for t in targets))
        return 0

    logdir = Path(os.environ.get("SMOKE_LOG_DIR") or Path(tempfile.gettempdir()) / "smoke-logs")
    logdir.mkdir(parents=True, exist_ok=True)
    results: list[Result] = []
    try:
        for t in targets:
            results.append(run_target(t, args, logdir))
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
    failed = [r for r in results if not r.ok]
    print(f"\npassed: {len(results) - len(failed)}  failed: {len(failed)}  (logs: {logdir})")
    for r in failed:
        print(f"  FAILED {r.target}: {r.note}")
    if args.report:
        Path(args.report).write_text(json.dumps(
            [{"target": r.target, "ok": r.ok, "seconds": round(r.seconds), "note": r.note, "log": str(r.log)} for r in results],
            indent=2), encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
