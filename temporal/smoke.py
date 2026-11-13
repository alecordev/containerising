# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Cluster health, default namespace, then start a workflow (no worker needed), see it RUNNING, terminate it."""
import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import dc, expect, http, port, retry, run, step  # noqa: E402

WF_ID = "smoke-wf"


def temporal(*args: str) -> str:
    """Run the temporal CLI in a one-shot admin-tools container on the compose network."""
    return dc(
        "run", "--rm", "-T", "--no-deps", "--entrypoint", "temporal", "create-namespace",
        "--address", "temporal:7233", *args, timeout=180,
    ).stdout


def main() -> None:
    step("cluster health + default namespace")
    temporal("operator", "cluster", "health")
    temporal("operator", "namespace", "describe", "-n", "default")

    step("start workflow, expect RUNNING")
    temporal("workflow", "start", "--type", "SmokeWorkflow", "--task-queue", "smoke-queue",
             "--workflow-id", WF_ID, "--input", '"hi"')
    out = retry(lambda: temporal("workflow", "describe", "--workflow-id", WF_ID, "-o", "json"), timeout=30, desc="describe")
    expect("WORKFLOW_EXECUTION_STATUS_RUNNING" in out, f"workflow not RUNNING:\n{out[:500]}")

    step("terminate workflow, expect TERMINATED")
    temporal("workflow", "terminate", "--workflow-id", WF_ID, "--reason", "smoke-test")
    out = temporal("workflow", "describe", "--workflow-id", WF_ID, "-o", "json")
    expect("WORKFLOW_EXECUTION_STATUS_TERMINATED" in out, f"workflow not TERMINATED:\n{out[:500]}")

    step("UI health")
    http(f"http://localhost:{port('TEMPORAL_UI_PORT', 8233)}/healthz")


run(main)
