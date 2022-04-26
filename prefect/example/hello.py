import prefect
from prefect import task, Flow


@task
def hello_task():
    logger = prefect.context.get("logger")
    logger.info("Hello world!")


with Flow("hello-flow") as flow:
    hello_task()

flow.run()
