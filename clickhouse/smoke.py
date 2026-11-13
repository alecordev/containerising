# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Live check: create a MergeTree table, insert rows, count them, and call the HTTP interface."""
from urllib.parse import quote

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, http, port, run  # noqa: E402

USER = env("CLICKHOUSE_USER", "clickhouse")
PASSWORD = env("CLICKHOUSE_PASSWORD", "clickhouse")


def ch(query: str) -> str:
    return exec_("clickhouse", "clickhouse-client", "--user", USER, "--password", PASSWORD, "-q", query).stdout.strip()


def main() -> None:
    ch("CREATE TABLE IF NOT EXISTS smoke (id UInt32, name String) ENGINE = MergeTree ORDER BY id")
    ch("TRUNCATE TABLE smoke")
    ch("INSERT INTO smoke VALUES (1, 'hello'), (2, 'world')")
    count = ch("SELECT count() FROM smoke")
    expect(count == "2", f"expected 2 rows, got {count!r}")

    url = f"http://localhost:{port('CLICKHOUSE_HTTP_PORT', 8123)}/?user={quote(USER)}&password={quote(PASSWORD)}"
    body = http(url, "POST", data="SELECT 1").body.strip()
    expect(body == "1", f"HTTP interface returned {body!r}")
    ch("DROP TABLE smoke")


run(main)
