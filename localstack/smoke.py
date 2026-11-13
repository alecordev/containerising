# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Exercise S3, SQS and DynamoDB on the moto mock through the AWS CLI (one-shot `aws` container)."""
import json
import time

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import dc, expect, http, port, run, step  # noqa: E402


def aws(*args: str, input: str | None = None) -> str:
    return dc("run", "--rm", "-T", "aws", *args, input=input, timeout=180).stdout.strip()


def main() -> None:
    bucket = f"smoke-{int(time.time())}"

    step("S3: bucket, put, get")
    aws("s3", "mb", f"s3://{bucket}")
    aws("s3", "cp", "-", f"s3://{bucket}/hello.txt", input="hello aws\n")
    expect(aws("s3", "cp", f"s3://{bucket}/hello.txt", "-") == "hello aws", "S3 round trip failed")

    step("SQS: create queue, send, receive")
    queue = aws("sqs", "create-queue", "--queue-name", "smoke-queue", "--query", "QueueUrl", "--output", "text")
    aws("sqs", "send-message", "--queue-url", queue, "--message-body", "ping")
    body = aws("sqs", "receive-message", "--queue-url", queue, "--query", "Messages[0].Body", "--output", "text")
    expect(body == "ping", f"SQS receive returned {body!r}")

    step("DynamoDB: table, put, get")
    aws("dynamodb", "create-table", "--table-name", "smoke", "--attribute-definitions", "AttributeName=id,AttributeType=S",
        "--key-schema", "AttributeName=id,KeyType=HASH", "--billing-mode", "PAY_PER_REQUEST")
    aws("dynamodb", "put-item", "--table-name", "smoke", "--item", json.dumps({"id": {"S": "1"}, "v": {"S": "x"}}))
    value = aws("dynamodb", "get-item", "--table-name", "smoke", "--key", json.dumps({"id": {"S": "1"}}),
                "--query", "Item.v.S", "--output", "text")
    expect(value == "x", f"DynamoDB get-item returned {value!r}")

    step("host-side reachability of the published port")
    http(f"http://localhost:{port('MOTO_PORT', 4566)}/moto-api/")


run(main)
