# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "temporalio==1.36.0",
# ]
# ///

"""Example worker: serves HelloWorkflow + say_hello on the `hello-task-queue`."""
import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from workflows import TASK_QUEUE, HelloWorkflow, say_hello


async def main() -> None:
    client = await Client.connect(
        os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
    )
    async with Worker(client, task_queue=TASK_QUEUE, workflows=[HelloWorkflow], activities=[say_hello]):
        print(f"worker listening on task queue {TASK_QUEUE!r}", flush=True)
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
