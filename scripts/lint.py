#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Static repo checks. Nothing is started. Python 3.10+ standard library only; cross-platform.

Checks:
  * every compose file passes ``docker compose config -q`` (uses .env.example when there is no .env)
  * no ``version:`` key and no ``:latest`` image tag in compose files (opt out per line: ``# lint: allow-latest``)
  * every Python file compiles (in memory, writes no ``__pycache__``)
  * a Dockerfile has a .dockerignore (or ``<Dockerfile>.dockerignore``) next to it; blacklist-style ignore files
    must also exclude the uv/smoke files (pyproject.toml, uv.lock, smoke*.py, .venv)
  * every service directory (one with a compose file) has a README.md
  * no oddly named files/dirs (e.g. ``scripts;C`` left behind by a mangled Windows bind mount)
  * no legacy bash ``.smoke`` files; ``.sh`` files are only allowed if a compose file or Dockerfile in
    the same service references them (i.e. they run inside Linux containers)
  * every smoke*.py compiles and carries the sys.path bootstrap that lets it run on its own
  * every top-level service directory is mentioned in README.md and AGENTS.md
  * uv projects (pyproject.toml + PEP 723 script headers) match their requirements.txt (see sync_uv.py)
  * READMEs show uv instead of plain ``pip install`` / ``python -m venv``

Usage: python scripts/lint.py [--no-docker]
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".docker", "output"}
GOOD_NAME = re.compile(r"^[A-Za-z0-9._\-+@=,~]+$")
ALLOWED_ODD: set[str] = set()
problems: list[str] = []


def bad(kind: str, path: Path | str, msg: str = "") -> None:
    problems.append(f"{kind:<14} {Path(path).as_posix()} {msg}".rstrip())


def walk() -> list[tuple[Path, list[str], list[str]]]:
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS or d == "output")
        if Path(dirpath).name == "output":
            dirnames[:] = []
        out.append((Path(dirpath), dirnames, sorted(filenames)))
    return out


def is_compose(name: str) -> bool:
    return ".override." not in name and (
        name in ("compose.yml", "compose.yaml") or (name.startswith("docker-compose") and name.endswith((".yml", ".yaml")))
    )


def main() -> int:
    no_docker = "--no-docker" in sys.argv
    tree = walk()
    for dirpath, dirnames, filenames in tree:
        rel = dirpath.relative_to(ROOT)
        for n in [*dirnames, *filenames]:
            if n not in ALLOWED_ODD and not GOOD_NAME.match(n):
                bad("odd-name", rel / n)
        compose_files = [f for f in filenames if is_compose(f)]
        if compose_files and rel.parts[:1] != ("templates",):
            if not any((ROOT / Path(*rel.parts[:i]) / "README.md").exists() for i in range(len(rel.parts), 0, -1)):
                bad("no-readme", rel, "(a README.md in this dir or a parent dir is required)")
        if "Dockerfile" in filenames or any(f.startswith("Dockerfile") for f in filenames):
            dockerfiles = [f for f in filenames if f.startswith("Dockerfile") and not f.endswith((".dockerignore", ".example"))]
            has_ignore = ".dockerignore" in filenames or any(f.endswith(".dockerignore") and f != ".dockerignore" for f in filenames)
            if dockerfiles and not has_ignore:
                bad("no-dockerignore", rel, f"({', '.join(dockerfiles)})")
        for ign in (x for x in filenames if x.endswith("dockerignore") and not x.endswith(".example")):
            lines = [ln.strip() for ln in (dirpath / ign).read_text(encoding="utf-8", errors="replace").splitlines()]
            if "*" not in lines:  # blacklist style: anything not listed is sent to the daemon and may be COPY'd
                missing = [k for k in ("pyproject.toml", "uv.lock", "smoke*.py", ".venv") if k not in lines]
                if missing:
                    bad("dockerignore", rel / ign, f"(blacklist style: also exclude {', '.join(missing)}; or switch to a '*' whitelist)")
        # compose checks
        texts = ""
        for f in compose_files:
            p = dirpath / f
            text = p.read_text(encoding="utf-8", errors="replace")
            texts += text
            if re.search(r"^version:", text, re.M):
                bad("version-key", rel / f)
            for line in text.splitlines():
                m = re.match(r"^\s*image:\s*([^\s#]+)", line)
                if m and m.group(1).endswith(":latest") and "lint: allow-latest" not in line:
                    bad("latest-tag", rel / f, m.group(1) + "  (add '# lint: allow-latest' + a reason if unavoidable)")
            if not no_docker:
                env = [] if (dirpath / ".env").exists() else (["--env-file", ".env.example"] if (dirpath / ".env.example").exists() else [])
                r = subprocess.run(["docker", "compose", *env, "-f", f, "config", "-q"], cwd=dirpath, capture_output=True, text=True)
                if r.returncode != 0:
                    bad("compose-config", rel / f, (r.stderr.strip().splitlines() or ["?"])[-1][:160])
        for f in filenames:
            p = dirpath / f
            if f == ".smoke" or f.endswith(".smoke"):
                bad("legacy-smoke", rel / f, "(convert to smoke.py using scripts/smokelib.py)")
            if f.endswith(".sh"):
                dockerfile_text = "".join((dirpath / g).read_text(errors="replace") for g in filenames if g.startswith("Dockerfile"))
                if f not in texts and f not in dockerfile_text and not any(f in (dirpath.parent / g).read_text(errors="replace") for g in os.listdir(dirpath.parent) if is_compose(g)):
                    bad("host-shell", rel / f, "(host-side scripts must be Python; .sh only for scripts run inside containers)")
            if f.startswith("smoke") and f.endswith(".py") and dirpath != ROOT / "scripts":
                if '"smokelib.py").is_file()' not in p.read_text(encoding="utf-8", errors="replace"):
                    bad("smoke-bootstrap", rel / f, "(copy the sys.path bootstrap from templates/service/smoke.py)")
            if f.endswith(".py"):
                try:
                    compile(p.read_text(encoding="utf-8"), str(p), "exec")
                except SyntaxError as e:
                    bad("py-syntax", rel / f, f"line {e.lineno}: {e.msg}")
    # every top-level service directory must be mentioned in the root README.md and AGENTS.md
    docs = {n: (ROOT / n).read_text(encoding="utf-8") for n in ("README.md", "AGENTS.md") if (ROOT / n).exists()}
    top = sorted({d.relative_to(ROOT).parts[0] for d, _, files in tree if any(is_compose(f) for f in files) and d != ROOT})
    for name in top:
        if name == "templates":
            continue
        for doc, text in docs.items():
            if f"`{name}/" not in text and f"`{name}`" not in text:
                bad("undocumented", name, f"(not mentioned in {doc})")
    # uv: every pyproject.toml / script header must match its requirements.txt (python scripts/sync_uv.py fixes it)
    sys.path.insert(0, str(ROOT / "scripts"))
    import sync_uv

    for rel in sync_uv.sync(check=True):
        bad("uv-out-of-date", rel, "(run: python scripts/sync_uv.py)")

    # READMEs show uv, not plain pip/venv (a line may mention pip if it also mentions uv, --prefix, legacy, ...)
    pip_re = re.compile(r"pip3? install|python3? -m venv|\.venv\S*[/\\](?:bin|Scripts)")
    ok_re = re.compile(r"\buv\b|--prefix|still works|also works|legacy")
    for dirpath, _, filenames in tree:
        if "README.md" in filenames:
            for n, line in enumerate((dirpath / "README.md").read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if pip_re.search(line) and not ok_re.search(line):
                    bad("readme-pip", (dirpath / "README.md").relative_to(ROOT), f"line {n}: use uv (uv run / uv add / uv sync)")
    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s)")
        return 1
    print("lint ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
