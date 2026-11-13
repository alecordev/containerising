# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Start the demo database too, then log in through Adminer's own login form (cookie session)."""
import http.cookiejar
import re
import urllib.parse
import urllib.request

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import SmokeError, dc, expect, port, retry, run, step  # noqa: E402


def login_and_read(base: str) -> str:
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(jar))
    landing = opener.open(base + "/", timeout=20).read().decode("utf-8", "replace")
    expect("adminer" in landing.lower(), "Adminer landing page not served")
    form = {"auth[driver]": "pgsql", "auth[server]": "demo-postgres", "auth[username]": "demo",
            "auth[password]": "demo", "auth[db]": "demo"}
    # Adminer 5+/6 may add a CSRF-style token field to the login form: forward any hidden inputs.
    for name, value in re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\']', landing):
        form.setdefault(name, value)
    resp = opener.open(urllib.request.Request(base + "/", data=urllib.parse.urlencode(form).encode()), timeout=30)
    return resp.read().decode("utf-8", "replace")


def main() -> None:
    try:
        step("start the demo Postgres (profile 'demo')")
        dc("--profile", "demo", "up", "-d", "--wait", timeout=300)
        base = f"http://localhost:{port('ADMINER_PORT', 8082)}"
        step("log in through Adminer")
        page = retry(lambda: login_and_read(base), timeout=30, interval=3, desc="Adminer login")
        if not re.search(r"logout|SQL command|Select database", page, re.I):
            raise SmokeError(f"login did not reach the database page:\n{page[:600]}")
    finally:
        # The runner's own `down` does not know the 'demo' profile: clean it (and its volume) here.
        dc("--profile", "demo", "down", "-v", "--remove-orphans", check=False, timeout=180)


run(main)
