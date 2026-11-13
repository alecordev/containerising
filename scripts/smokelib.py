"""Helpers for per-service smoke tests. Python 3.10+ standard library only, works on Linux/macOS/Windows.

A service directory may contain ``smoke.py`` (for its ``docker-compose.yml``) or
``smoke.<compose-file-stem>.py`` (for another compose file, e.g. ``smoke.docker-compose_cluster.py``).
``scripts/smoke.py`` runs it AFTER ``docker compose up -d --wait``, with:

* the working directory set to the service directory,
* ``scripts/`` on ``PYTHONPATH`` (so ``from smokelib import ...`` works),
* ``SMOKE_DC`` set to the project-scoped compose command as JSON (used by :func:`dc`).

A smoke test must exercise the service for real (write+read, query, API call) and raise or
``sys.exit(1)`` on failure. Keep it quick (< 60-90 s).

Every smoke file also runs **on its own** against a stack you already started (``python smoke.py`` /
``uv run smoke.py``, from any directory): it puts ``scripts/`` on ``sys.path`` itself, then this module
runs from the file's directory, reads that directory's ``.env``, and targets the compose file next to it.

Typical use::

    from smokelib import exec_, http, port, expect, retry, run

    def main():
        out = exec_("db", "psql", "-U", "postgres", "-tAc", "select 42").stdout
        expect("42" in out, f"unexpected psql output: {out!r}")
        r = http(f"http://localhost:{port('PG_UI_PORT', 8080)}/health")
        expect(r.json()["status"] == "ok", "health not ok")

    run(main)
"""
from __future__ import annotations

import base64
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

__all__ = [
    "DC", "SmokeError", "Response", "env", "port", "dc", "exec_", "sh", "run_container",
    "http", "retry", "expect", "step", "run",
]

COMPOSE_NAMES = ("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")


def _script_dir() -> Path:
    main_file = getattr(sys.modules.get("__main__"), "__file__", None)
    return Path(main_file).resolve().parent if main_file else Path.cwd()


def _standalone_dc(script_dir: Path) -> list[str]:
    """Compose command for running a smoke file directly: the compose file that belongs to it.

    ``smoke.py`` -> docker-compose.yml (or compose.yml); ``smoke.<stem>.py`` -> ``<stem>.yml``. No project name is
    given, so it targets the stack you started yourself with plain ``docker compose up`` in that directory.
    """
    name = Path(getattr(sys.modules.get("__main__"), "__file__", "smoke.py")).name
    stem = name[len("smoke."):-len(".py")] if name.startswith("smoke.") and name != "smoke.py" else ""
    candidates = [f"{stem}{ext}" for ext in (".yml", ".yaml")] if stem else list(COMPOSE_NAMES)
    for c in candidates:
        if (script_dir / c).is_file():
            return ["docker", "compose", "--project-directory", str(script_dir), "-f", str(script_dir / c)]
    return ["docker", "compose", "--project-directory", str(script_dir)]


def _load_dotenv(path: Path) -> None:
    """Make the service's .env visible to port()/env() like compose sees it (existing variables win)."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


if "SMOKE_DC" in os.environ:  # started by scripts/smoke.py: project-scoped command, cwd already the service dir
    DC: list[str] = json.loads(os.environ["SMOKE_DC"])
else:  # run directly (python smoke.py / uv run smoke.py): behave the same from any working directory
    _dir = _script_dir()
    os.chdir(_dir)
    _load_dotenv(_dir / ".env")
    DC = _standalone_dc(_dir)


class SmokeError(AssertionError):
    """A smoke check failed."""


def env(name: str, default: str = "") -> str:
    """Environment variable with a default (mirrors compose ``${NAME:-default}``)."""
    return os.environ.get(name) or default


def port(name: str, default: int) -> int:
    """Host port from the environment, falling back to the compose default."""
    return int(env(name, str(default)))


def step(msg: str) -> None:
    print(f"-- {msg}", flush=True)


def expect(cond: object, msg: str = "expectation failed") -> None:
    if not cond:
        raise SmokeError(msg)


def _run(cmd: Sequence[str], *, input: str | None = None, check: bool = True, timeout: float = 120) -> subprocess.CompletedProcess:
    p = subprocess.run(
        list(cmd), input=input, capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout,
    )
    if check and p.returncode != 0:
        raise SmokeError(
            f"command failed (rc={p.returncode}): {' '.join(cmd)}\n--- stdout ---\n{p.stdout}\n--- stderr ---\n{p.stderr}"
        )
    return p


def dc(*args: str, input: str | None = None, check: bool = True, timeout: float = 120) -> subprocess.CompletedProcess:
    """Run ``docker compose <args>`` scoped to the smoke project/compose file."""
    return _run([*DC, *args], input=input, check=check, timeout=timeout)


def exec_(service: str, *cmd: str, input: str | None = None, check: bool = True, timeout: float = 120) -> subprocess.CompletedProcess:
    """``docker compose exec -T <service> <cmd...>`` (no TTY, safe in CI)."""
    return dc("exec", "-T", service, *cmd, input=input, check=check, timeout=timeout)


def sh(service: str, script: str, *, check: bool = True, timeout: float = 120) -> subprocess.CompletedProcess:
    """Run a shell snippet INSIDE a (Linux) container: ``exec -T <service> sh -c <script>``."""
    return exec_(service, "sh", "-c", script, check=check, timeout=timeout)


def run_container(service: str, *cmd: str, check: bool = True, timeout: float = 300) -> subprocess.CompletedProcess:
    """``docker compose run --rm -T <service> <cmd...>`` for one-shot client containers."""
    return dc("run", "--rm", "-T", service, *cmd, check=check, timeout=timeout)


@dataclass
class Response:
    status: int
    body: str
    headers: Mapping[str, str] = field(default_factory=dict)

    def json(self) -> Any:
        return json.loads(self.body)


def http(
    url: str,
    method: str = "GET",
    *,
    data: str | bytes | None = None,
    json_body: Any = None,
    headers: Mapping[str, str] | None = None,
    auth: tuple[str, str] | None = None,
    timeout: float = 30,
    ok: Iterable[int] | range = range(200, 300),
    verify: bool = True,
) -> Response:
    """Tiny HTTP client. Raises SmokeError unless the status is in ``ok``; returns status/body/headers."""
    hdrs = dict(headers or {})
    payload: bytes | None
    if json_body is not None:
        payload = json.dumps(json_body).encode()
        hdrs.setdefault("Content-Type", "application/json")
    elif isinstance(data, str):
        payload = data.encode()
    else:
        payload = data
    if auth:
        hdrs["Authorization"] = "Basic " + base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
    ctx = None if verify else ssl._create_unverified_context()  # noqa: S323 - dev self-signed certs
    # Never go through a corporate proxy for localhost checks.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(url, data=payload, method=method, headers=hdrs)
    try:
        with opener.open(req, timeout=timeout) as resp:
            status, body, rh = resp.status, resp.read().decode("utf-8", "replace"), dict(resp.headers)
    except urllib.error.HTTPError as e:
        status, body, rh = e.code, e.read().decode("utf-8", "replace"), dict(e.headers)
    except (urllib.error.URLError, OSError) as e:
        raise SmokeError(f"{method} {url} failed: {e}") from e
    if status not in ok:
        raise SmokeError(f"{method} {url} -> HTTP {status}\n{body[:1000]}")
    return Response(status, body, rh)


def retry(fn: Callable[[], Any], *, timeout: float = 60, interval: float = 2, desc: str = "condition") -> Any:
    """Call ``fn`` until it returns a truthy value without raising; return that value or fail after ``timeout`` s."""
    deadline = time.monotonic() + timeout
    last: BaseException | None = None
    while True:
        try:
            result = fn()
            if result:
                return result
            last = None
        except Exception as e:  # noqa: BLE001 - we report the last one
            last = e
        if time.monotonic() >= deadline:
            raise SmokeError(f"timed out after {timeout}s waiting for {desc}" + (f": {last}" if last else ""))
        time.sleep(interval)


def run(main: Callable[[], None]) -> None:
    """Entry point: run ``main`` and exit non-zero with a readable message on failure."""
    try:
        main()
    except SmokeError as e:
        print(f"SMOKE FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired as e:
        print(f"SMOKE FAILED: timeout: {e}", file=sys.stderr)
        sys.exit(1)
    print("smoke ok")
