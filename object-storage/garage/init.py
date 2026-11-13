#!/usr/bin/env python3
"""One-shot bootstrap for a single-node Garage: assign the layout, import a dev key, create a bucket.

Idempotent: safe to re-run (it is, on every `docker compose up`). Runs inside the garage-dev image
(Alpine + python3 + the `garage` binary); standard library only.
"""
import os
import subprocess
import sys
import time


def need(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        sys.exit(f"{name} is required")
    return value


ACCESS_KEY, SECRET_KEY, BUCKET = need("GARAGE_ACCESS_KEY"), need("GARAGE_SECRET_KEY"), need("GARAGE_BUCKET")
CAPACITY = os.environ.get("GARAGE_CAPACITY", "1G")

# `garage node id -q` prints <node-id>@<rpc_public_addr>, read from the metadata volume + garage.toml
NODE_ADDR = subprocess.run(["garage", "node", "id", "-q"], capture_output=True, text=True, check=True).stdout.strip()
NODE_ID = NODE_ADDR.split("@", 1)[0]


def g(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["garage", "-h", NODE_ADDR, *args], capture_output=True, text=True, check=check)


def ok(*args: str) -> bool:
    return g(*args, check=False).returncode == 0


print(f"Waiting for the node at {NODE_ADDR.split('@', 1)[-1]} ...", flush=True)
for _ in range(30):
    if ok("status"):
        break
    time.sleep(1)
else:
    sys.exit("garage not reachable")

# Layout: only assign when this node has no role yet
if NODE_ID[:16] in g("layout", "show", check=False).stdout:
    print("Layout already contains this node.")
else:
    print(f"Assigning layout (zone dc1, capacity {CAPACITY}) ...")
    g("layout", "assign", "-z", "dc1", "-c", CAPACITY, NODE_ID)
    g("layout", "apply", "--version", "1")

# Key: import a fixed key so S3 clients can use known credentials
if ok("key", "info", "dev-key"):
    print("Key dev-key exists.")
else:
    g("key", "import", "--yes", "-n", "dev-key", ACCESS_KEY, SECRET_KEY)

# Allow the key to create buckets through the S3 API (off by default in Garage)
g("key", "allow", "--create-bucket", "dev-key")

# Bucket + permissions
if ok("bucket", "info", BUCKET):
    print(f"Bucket {BUCKET} exists.")
else:
    g("bucket", "create", BUCKET)
g("bucket", "allow", "--read", "--write", "--owner", BUCKET, "--key", "dev-key")

print(f"Garage ready: bucket '{BUCKET}', key {ACCESS_KEY}")
