# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Wait for the connector, change a row in Postgres, and read the change event back from Kafka."""
import time

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, http, port, retry, run  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('CONNECT_PORT', 8083)}"

    def connector_running() -> bool:
        d = http(f"{base}/connectors/inventory-connector/status").json()
        return d["connector"]["state"] == "RUNNING" and bool(d["tasks"]) and all(t["state"] == "RUNNING" for t in d["tasks"])

    retry(connector_running, timeout=120, interval=3, desc="inventory-connector and its tasks to be RUNNING")

    email = f"smoke-{int(time.time())}@example.com"
    exec_("postgres", "psql", "-U", env("POSTGRES_USER", "postgres"), "-d", env("POSTGRES_DB", "inventory"),
          "-v", "ON_ERROR_STOP=1", "-c",
          f"INSERT INTO customers (first_name, last_name, email) VALUES ('Smoke', 'Test', '{email}')")

    # --from-beginning replays the snapshot too; the consumer exits after 20 s without new messages
    # (that timeout makes it exit non-zero, hence check=False; the assertion is on the output).
    out = exec_("kafka", "/opt/kafka/bin/kafka-console-consumer.sh", "--bootstrap-server", "localhost:9092",
                "--topic", "dbserver1.public.customers", "--from-beginning", "--timeout-ms", "20000",
                check=False, timeout=180).stdout
    expect(email in out, f"change event for {email} not found on dbserver1.public.customers")


run(main)
