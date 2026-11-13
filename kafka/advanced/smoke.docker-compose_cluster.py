# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: create a replicated topic on the 3-node cluster, produce one message and consume it back."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, run  # noqa: E402

SERVICE = "kafka-1"
K = "/opt/kafka/bin"
# INTERNAL listeners: with `localhost:9092` the producer would be redirected to other brokers' host-facing
# addresses (localhost:9094/9096), which do not exist inside the kafka-1 container.
BOOT = "kafka-1:19092,kafka-2:19092,kafka-3:19092"


def main() -> None:
    exec_(SERVICE, f"{K}/kafka-topics.sh", "--bootstrap-server", BOOT, "--create", "--if-not-exists",
          "--topic", "smoke", "--partitions", "3", "--replication-factor", "3")
    exec_(SERVICE, f"{K}/kafka-console-producer.sh", "--bootstrap-server", BOOT, "--topic", "smoke", input="hello" + chr(10))
    out = exec_(SERVICE, f"{K}/kafka-console-consumer.sh", "--bootstrap-server", BOOT, "--topic", "smoke",
                "--from-beginning", "--max-messages", "1", "--timeout-ms", "30000").stdout
    expect("hello" in out, f"consumer output: {out!r}")


run(main)
