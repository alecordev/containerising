"""Minimal Airflow 3 DAG used to verify the stack works end to end."""

from __future__ import annotations

import pendulum
from airflow.sdk import dag, task


@dag(
    dag_id="hello_airflow",
    schedule=None,
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)
def hello_airflow():
    @task
    def extract() -> list[int]:
        return [1, 2, 3]

    @task
    def total(values: list[int]) -> int:
        result = sum(values)
        print(f"sum={result}")
        return result

    total(extract())


hello_airflow()
