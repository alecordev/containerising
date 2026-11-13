# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "prefect>=3.9,<4",
# ]
# ///

"""Prefect 3 hello-world.

    pip install -r requirements.txt
    python hello.py            # run once locally (ephemeral run, shown in the UI if PREFECT_API_URL is set)
    python hello.py serve      # register a deployment and keep serving it (runs every minute)

Point the client at the dockerised server first:
    export PREFECT_API_URL=http://localhost:4200/api      (PowerShell: $env:PREFECT_API_URL=...)
"""

import sys

from prefect import flow, get_run_logger, task


@task(retries=2, retry_delay_seconds=1)
def hello_task(name: str) -> str:
    logger = get_run_logger()
    logger.info("Hello %s!", name)
    return f"Hello {name}"


@flow(name="hello-flow", log_prints=True)
def hello_flow(name: str = "world") -> str:
    message = hello_task(name)
    print(message)
    return message


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        hello_flow.serve(name="hello-every-minute", cron="* * * * *")
    else:
        hello_flow()
