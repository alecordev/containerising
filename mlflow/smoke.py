# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Create an experiment and a run through the REST API, log a metric, upload an artifact through the proxy."""
import time

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, run  # noqa: E402


def main() -> None:
    base = f"http://localhost:{port('MLFLOW_PORT', 5000)}"
    api = f"{base}/api/2.0/mlflow"

    exp_id = http(f"{api}/experiments/create", "POST", json_body={"name": f"smoke-{int(time.time())}"}).json()["experiment_id"]
    run_id = http(f"{api}/runs/create", "POST", json_body={"experiment_id": exp_id, "start_time": 1}).json()["run"]["info"]["run_id"]
    http(f"{api}/runs/log-metric", "POST", json_body={"run_id": run_id, "key": "rmse", "value": 0.42, "timestamp": 1})

    # artifacts go through the tracking server (--serve-artifacts), no S3/volume access needed by clients
    http(f"{api}-artifacts/artifacts/{exp_id}/{run_id}/artifacts/note.txt", "PUT", data=b"hi\n",
         headers={"Content-Type": "application/octet-stream"})

    got = http(f"{api}/runs/get?run_id={run_id}").json()["run"]["data"]["metrics"]
    expect(any(m["key"] == "rmse" for m in got), f"metric rmse not stored: {got}")
    listing = http(f"{api}/artifacts/list?run_id={run_id}").json()
    expect(any(f["path"] == "note.txt" for f in listing.get("files", [])), f"artifact not listed: {listing}")


run(main)
