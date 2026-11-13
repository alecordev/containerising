# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "temporalio==1.36.0",
# ]
# ///

"""Start HelloWorkflow and print its result (needs the worker running)."""
import asyncio
import os
import sys
import uuid

from temporalio.client import Client

from workflows import TASK_QUEUE, HelloWorkflow


async def main() -> None:
    client = await Client.connect(
        os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
    )
    name = sys.argv[1] if len(sys.argv) > 1 else "Temporal"
    result = await client.execute_workflow(
        HelloWorkflow.run, name, id=f"hello-{uuid.uuid4()}", task_queue=TASK_QUEUE
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
