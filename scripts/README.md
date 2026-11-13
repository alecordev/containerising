# scripts/

Repo tooling. **Python 3.10+, standard library only, no install step**, and no bash anywhere on the host side, so the same commands work on Linux, macOS and Windows (PowerShell, cmd or Git Bash). Run everything from the repo root.

| Script | Purpose |
|---|---|
| `smoke.py` | Start each compose stack, run its live check, tear it down |
| `smokelib.py` | Helper library imported by every service `smoke.py` (stdlib only, found automatically; see below) |
| `lint.py` | Static repo checks (nothing is started) |
| `ports.py` | Published host ports, clashes, free-port finder |
| `new_service.py` | Scaffold a new service directory from `templates/service` |
| `sync_uv.py` | Keep every Python example uv-ready: generate `pyproject.toml` and PEP 723 headers from `requirements.txt` |

## smoke.py: run the stacks

```bash
python scripts/smoke.py --list                 # what would run
python scripts/smoke.py postgresql redis       # specific directories
python scripts/smoke.py kafka/advanced/docker-compose_cluster.yml   # a specific compose file
python scripts/smoke.py                        # everything, sequentially (hours; needs lots of disk/RAM)
python scripts/smoke.py --rmi -x oracle-free   # remove images afterwards, skip a heavy one
```

For each target it runs `docker compose -p smoke up -d --build --wait`, then the service's smoke test (if any), then `down -v --remove-orphans`. It uses the project name `smoke` and **never touches other compose projects or containers**. Targets run one at a time; many templates share host ports and some need several GB of RAM.

Options: `-l/--list`, `-k/--keep` (leave it running, for one target), `-r/--rmi` (delete images afterwards to save disk), `-w/--wait SECONDS` (healthcheck timeout, default 300), `-p/--project NAME`, `-x/--exclude TEXT` (repeatable), `--report FILE` (JSON summary). Logs go to `<tmp>/smoke-logs/` (`SMOKE_LOG_DIR` to change). Exit code is non-zero when any target fails. Directories containing a `.smoke-skip` file are skipped by default (one-shot app images that exit by design).

If a directory has a `.env` it is used, otherwise `.env.example` (so the defaults are exercised).

### Writing a smoke test

Put `smoke.py` in the service directory (or `smoke.<compose-file-stem>.py` for another compose file, e.g. `smoke.docker-compose_cluster.py`). It must really exercise the service (write+read, query, API call), finish in under about 90 s, and fail by raising or exiting non-zero.

**Every smoke file runs two ways, from any directory:**

```bash
python scripts/smoke.py valkey      # the runner: up --wait, run the check, tear everything down (project "smoke")
python valkey/smoke.py              # just the check, against a stack you started yourself with `docker compose up`
uv run valkey/smoke.py              # same, and uv picks a suitable Python (the file carries a PEP 723 header)
```

How that works, so there is no `requirements.txt` and no packaging:

- Each file starts with a 3-line **bootstrap** that finds the repo's `scripts/` directory from wherever the file lives and puts it on `sys.path`, then imports `smokelib`. Copy it from `templates/service/smoke.py`; `lint.py` fails if it is missing.
- Under the runner, `smokelib` uses the project-scoped compose command the runner passes in `SMOKE_DC`.
- Run directly, `smokelib` changes into the file's directory, reads that directory's `.env` (so custom ports are honoured, existing environment variables win) and targets the compose file next to the smoke file (`smoke.py` -> `docker-compose.yml`, `smoke.<stem>.py` -> `<stem>.yml`) with no project name, i.e. the stack you started yourself.

```python
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, http, port, retry, run  # noqa: E402

def main() -> None:
    out = exec_("db", "psql", "-U", "postgres", "-tAc", "select 42").stdout   # runs INSIDE the container
    expect("42" in out, f"unexpected output {out!r}")
    health = http(f"http://localhost:{port('API_PORT', 8080)}/health").json()  # host port, with compose default
    expect(health["status"] == "ok")
    retry(lambda: http(f"http://localhost:{port('API_PORT', 8080)}/ready").body == "ready", timeout=60, desc="ready")

run(main)
```

`smokelib` API: `dc(*args)`, `exec_(service, *cmd, input=None)` (`exec -T`), `sh(service, "shell snippet")` (inside the Linux container), `run_container(service, *cmd)` (one-shot `run --rm`), `http(url, method=, data=, json_body=, headers=, auth=(user, pw), ok=range, verify=)` returning `.status`, `.body`, `.headers`, `.json()`, `retry(fn, timeout=, interval=, desc=)`, `expect(cond, msg)`, `port(NAME, default)`, `env(NAME, default)`, `step(msg)`, `run(main)`. HTTP calls bypass proxies, so `localhost` checks work on corporate machines.

## lint.py: static checks

```bash
python scripts/lint.py             # includes `docker compose config -q` for every compose file
python scripts/lint.py --no-docker # skip the compose validation (no Docker needed)
```

Fails on: compose files that do not validate, a `version:` key, a `:latest` image (opt out per line with `# lint: allow-latest` plus a reason), Python that does not compile (checked in memory, no `__pycache__` written), a Dockerfile without a `.dockerignore`, a service directory without a README (itself or a parent), oddly named files such as `scripts;C` left behind by a mangled Windows bind mount, a smoke test without the `smokelib` bootstrap, leftover bash `.smoke` files, a pyproject/script header out of sync with `requirements.txt`, README instructions that use plain `pip install` / `python -m venv` instead of uv, host-side `.sh` files (container-side scripts referenced by a compose file or Dockerfile are allowed), and top-level service directories missing from `README.md` or `AGENTS.md`.

## ports.py: avoid port clashes

```bash
python scripts/ports.py --clashes        # who shares which host port
python scripts/ports.py --free 8000-8100 # unused ports, to pick a default for a new service
python scripts/ports.py --markdown       # table for docs
```

## new_service.py: scaffold

```bash
python scripts/new_service.py redpanda            # creates ./redpanda from templates/service
python scripts/new_service.py vectordb/qdrant --docker   # nested; also adds Dockerfile + .dockerignore
```

See [`templates/README.md`](../templates/README.md) for what you get.

## sync_uv.py: Python examples with uv

```bash
python scripts/sync_uv.py                    # (re)generate pyproject.toml + script headers for every uv project
python scripts/sync_uv.py --check            # exit 1 if anything is out of date (lint.py runs this)
python scripts/sync_uv.py --add my/examples  # register a directory that has a requirements.txt
python scripts/sync_uv.py --lock             # also run `uv lock` in each project (needs uv and network)
python scripts/sync_uv.py --list
```

A *uv project* is a directory with a `pyproject.toml` generated by this tool. Its `requirements.txt` is the only file you edit; the tool copies the dependencies into `pyproject.toml` and into a [PEP 723](https://peps.python.org/pep-0723/) `# /// script` block at the top of every example `.py` below it (subdirectories with their own `requirements.txt` are separate; `smoke*.py` are not example projects but get a dependency-free header so `uv run smoke.py` picks a suitable Python and never syncs a neighbouring project). That gives two ways to run the same example:

```bash
uv run src/simple.py          # from anywhere: dependencies come from the script header
uv sync && uv run python src/simple.py    # project environment from pyproject.toml (+ uv.lock)
```

`requires-python` in each `pyproject.toml` is preserved when you edit it by hand (default `>=3.11`, because current client libraries need it). The stdlib-only repo tools carry a header with `requires-python = ">=3.10"` so `uv run scripts/smoke.py` picks a suitable Python (downloading one if needed). Lockfiles (`uv.lock`) are committed; refresh them with `--lock`.

## Why Python and no bash

A bash script silently depends on GNU tools, path conversion and line endings; on Windows it breaks in subtle ways (a mangled bind mount once left a directory named `scripts;C` in this repo). Python behaves the same everywhere and is already required to run the examples. The only shell left in the repo runs **inside Linux containers** (for example `temporal/scripts/*.sh`, executed by an image that ships no Python), is referenced from compose, and is kept LF-only by `.gitattributes`.
