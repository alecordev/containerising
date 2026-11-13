# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Smoke test: broker is running; publish and fetch a message through the management API."""
from urllib.parse import quote

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, exec_, expect, http, port, retry, run  # noqa: E402


def main() -> None:
    exec_("rabbitmq", "rabbitmq-diagnostics", "-q", "check_running")
    base = f"http://localhost:{port('RABBITMQ_MANAGEMENT_PORT', 15672)}/api"
    auth = (env("RABBITMQ_DEFAULT_USER", "admin"), env("RABBITMQ_DEFAULT_PASS", "admin"))
    retry(lambda: http(f"{base}/overview", auth=auth), desc="management API")
    vhost = quote("/", safe="")
    # RabbitMQ 4 rejects transient non-exclusive queues, so declare it durable
    http(f"{base}/queues/{vhost}/smoke", "PUT", json_body={"durable": True, "auto_delete": False}, auth=auth)
    pub = http(f"{base}/exchanges/{vhost}/amq.default/publish", "POST", auth=auth, json_body={
        "properties": {}, "routing_key": "smoke", "payload": "hello", "payload_encoding": "string"})
    expect(pub.json().get("routed") is True, f"message was not routed: {pub.body}")
    got = http(f"{base}/queues/{vhost}/smoke/get", "POST", auth=auth, json_body={
        "count": 1, "ackmode": "ack_requeue_false", "encoding": "auto"}).json()
    expect(got and got[0]["payload"] == "hello", f"unexpected message: {got}")
    http(f"{base}/queues/{vhost}/smoke", "DELETE", auth=auth)


run(main)
