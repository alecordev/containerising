# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Bootstrap must have created layout, dev key and bucket; then a full put/get round trip over S3."""
import time

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import dc, env, exec_, expect, run, step  # noqa: E402


def aws(*args: str, input: str | None = None) -> str:
    return dc("run", "--rm", "-T", "aws", *args, input=input, timeout=180).stdout.strip()


def main() -> None:
    bucket = env("GARAGE_BUCKET", "dev")
    step("node is healthy and in layout")
    status = exec_("garage", "garage", "status").stdout.lower()
    expect("healthy" in status or "dc1" in status, f"unexpected `garage status`:\n{status}")
    step("bootstrap bucket exists")
    expect(bucket in aws("s3", "ls"), f"bucket {bucket!r} not found")
    step("put, list, get, delete")
    aws("s3", "cp", "-", f"s3://{bucket}/smoke.txt", input="hello object storage\n")
    expect("smoke.txt" in aws("s3", "ls", f"s3://{bucket}/"), "object not listed")
    expect(aws("s3", "cp", f"s3://{bucket}/smoke.txt", "-") == "hello object storage", "GET returned different data")
    aws("s3", "rm", f"s3://{bucket}/smoke.txt")
    step("create and remove a bucket through the S3 API")
    new_bucket = f"smoke-{int(time.time())}"
    aws("s3", "mb", f"s3://{new_bucket}")
    aws("s3", "rb", f"s3://{new_bucket}")


run(main)
