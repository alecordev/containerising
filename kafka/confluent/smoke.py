# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: create topic, produce+consume a message, register a schema in Schema Registry."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import exec_, expect, http, port, retry, run  # noqa: E402

BOOT = "localhost:9092"


def main() -> None:
    exec_("kafka", "kafka-topics", "--bootstrap-server", BOOT, "--create", "--if-not-exists",
          "--topic", "smoke", "--partitions", "1", "--replication-factor", "1")
    exec_("kafka", "kafka-console-producer", "--bootstrap-server", BOOT, "--topic", "smoke", input="hello\n")
    out = exec_("kafka", "kafka-console-consumer", "--bootstrap-server", BOOT, "--topic", "smoke",
                "--from-beginning", "--max-messages", "1", "--timeout-ms", "30000").stdout
    expect("hello" in out, f"consumer output: {out!r}")
    sr = f"http://localhost:{port('SCHEMA_REGISTRY_PORT', 8081)}"
    retry(lambda: http(f"{sr}/subjects"), desc="Schema Registry")
    hdr = {"Content-Type": "application/vnd.schemaregistry.v1+json"}
    http(f"{sr}/subjects/smoke-value/versions", "POST", json_body={"schema": '{"type":"string"}'}, headers=hdr)
    expect("smoke-value" in http(f"{sr}/subjects").json(), "schema subject not registered")
    http(f"{sr}/subjects/smoke-value", "DELETE")


run(main)
