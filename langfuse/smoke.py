# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Send an OpenTelemetry span with the bootstrapped API keys, then read it back through the v2 observations API.

Langfuse v4 runs in "events only" mode: traces are ingested via OTLP (POST /api/public/otel/v1/traces) and read
as observations (GET /api/public/v2/observations); the legacy /ingestion read endpoints (traces, scores) are gone.
Ingestion is asynchronous (web -> S3/Redis -> worker -> ClickHouse), so the read-back is retried.
"""
import secrets
import time

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import env, expect, http, port, retry, run  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('LANGFUSE_PORT', 3000)}"
    auth = (env("LANGFUSE_INIT_PROJECT_PUBLIC_KEY", "pk-lf-local"), env("LANGFUSE_INIT_PROJECT_SECRET_KEY", "sk-lf-local"))

    http(f"{base}/api/public/health")

    trace_id, span_id = secrets.token_hex(16), secrets.token_hex(8)
    now = time.time_ns()
    otlp = {"resourceSpans": [{
        "resource": {"attributes": [{"key": "service.name", "value": {"stringValue": "smoke"}}]},
        "scopeSpans": [{"scope": {"name": "smoke"}, "spans": [{
            "traceId": trace_id, "spanId": span_id, "name": "smoke-span", "kind": 1,
            "startTimeUnixNano": str(now - 10**9), "endTimeUnixNano": str(now),
        }]}],
    }]}
    http(f"{base}/api/public/otel/v1/traces", "POST", auth=auth, json_body=otlp,
         headers={"x-langfuse-ingestion-version": "4"})

    def stored() -> bool:
        data = http(f"{base}/api/public/v2/observations?traceId={trace_id}", auth=auth).json().get("data", [])
        return any(o.get("id") == span_id and o.get("name") == "smoke-span" for o in data)

    retry(stored, timeout=120, interval=3, desc=f"span {span_id} to appear in ClickHouse")


run(main)
