# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: create a topic, produce one message and consume it back (apache/kafka CLI tools in the container)."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, run  # noqa: E402

SERVICE = "kafka"
K = "/opt/kafka/bin"
BOOT = "localhost:9092"


def main() -> None:
    exec_(SERVICE, f"{K}/kafka-topics.sh", "--bootstrap-server", BOOT, "--create", "--if-not-exists",
          "--topic", "smoke", "--partitions", "1", "--replication-factor", "1")
    exec_(SERVICE, f"{K}/kafka-console-producer.sh", "--bootstrap-server", BOOT, "--topic", "smoke", input="hello" + chr(10))
    out = exec_(SERVICE, f"{K}/kafka-console-consumer.sh", "--bootstrap-server", BOOT, "--topic", "smoke",
                "--from-beginning", "--max-messages", "1", "--timeout-ms", "30000").stdout
    expect("hello" in out, f"consumer output: {out!r}")


run(main)
