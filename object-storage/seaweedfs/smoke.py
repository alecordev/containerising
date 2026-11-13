# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Create a bucket, PUT an object, GET it back, list, delete: all through the S3 API (aws-cli container)."""
import time

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import dc, expect, run, step  # noqa: E402


def aws(*args: str, input: str | None = None) -> str:
    return dc("run", "--rm", "-T", "aws", *args, input=input, timeout=180).stdout.strip()


def main() -> None:
    bucket = f"smoke-{int(time.time())}"
    step("make bucket")
    aws("s3", "mb", f"s3://{bucket}")
    step("put, list, get")
    aws("s3", "cp", "-", f"s3://{bucket}/hello.txt", input="hello object storage\n")
    expect("hello.txt" in aws("s3", "ls", f"s3://{bucket}/"), "object not listed")
    expect(aws("s3", "cp", f"s3://{bucket}/hello.txt", "-") == "hello object storage", "GET returned different data")
    step("delete object and bucket")
    aws("s3", "rm", f"s3://{bucket}/hello.txt")
    aws("s3", "rb", f"s3://{bucket}")


run(main)
