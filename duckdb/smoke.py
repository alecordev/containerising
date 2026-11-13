# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Run the CLI, the SQL example and the Python example inside the sandbox container."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, run  # noqa: E402


def main() -> None:
    expect("42" in exec_("duckdb", "duckdb", "-c", "SELECT 42 AS answer").stdout, "duckdb CLI query failed")
    expect("rows_in_parquet" in exec_("duckdb", "duckdb", "-f", "/work/examples/example.sql").stdout,
           "example.sql did not produce rows_in_parquet")
    expect("avg_price" in exec_("duckdb", "python", "/work/examples/example.py").stdout,
           "example.py did not produce avg_price")


run(main)
