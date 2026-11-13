# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Launch the example job through the GraphQL API and wait until the daemon + user code run it to SUCCESS."""
import time

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import SmokeError, expect, http, port, run, step  # noqa: E402

URL = f"http://localhost:{port('DAGSTER_PORT', 3000)}/graphql"


def gql(query: str, variables: dict | None = None) -> dict:
    body = http(URL, "POST", json_body={"query": query, "variables": variables or {}}, timeout=30).json()
    expect("errors" not in body, f"GraphQL errors: {body.get('errors')}")
    return body["data"]


def main() -> None:
    step("user-code location 'example' is loaded")
    nodes = gql("{ repositoriesOrError { __typename ... on RepositoryConnection { nodes { name location { name } } } } }")[
        "repositoriesOrError"
    ]["nodes"]
    expect(any(n["location"]["name"] == "example" for n in nodes), f"location 'example' missing: {nodes}")

    step("launch all_assets_job")
    launch = gql(
        """mutation($p: ExecutionParams!) { launchRun(executionParams: $p) {
             __typename
             ... on LaunchRunSuccess { run { runId } }
             ... on PythonError { message }
             ... on InvalidSubsetError { message }
             ... on RunConfigValidationInvalid { errors { message } } } }""",
        {"p": {"selector": {"repositoryLocationName": "example", "repositoryName": "__repository__",
                            "jobName": "all_assets_job"}, "runConfigData": {}}},
    )["launchRun"]
    expect(launch["__typename"] == "LaunchRunSuccess", f"launch failed: {launch}")
    run_id = launch["run"]["runId"]

    step(f"wait for run {run_id}")
    deadline = time.monotonic() + 150
    status = None
    while time.monotonic() < deadline:
        status = gql("query($id: ID!) { runOrError(runId: $id) { ... on Run { status } } }", {"id": run_id})["runOrError"]["status"]
        if status in ("SUCCESS", "FAILURE", "CANCELED"):
            break
        time.sleep(2)
    print(f"run {run_id} -> {status}")
    if status != "SUCCESS":
        raise SmokeError(f"run ended with status {status}")


run(main)
