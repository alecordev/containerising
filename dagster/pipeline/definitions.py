"""Minimal example code location: two assets, a job and a schedule."""
import dagster as dg


@dg.asset
def raw_numbers() -> list[int]:
    return list(range(1, 11))


@dg.asset
def total(context: dg.AssetExecutionContext, raw_numbers: list[int]) -> int:
    result = sum(raw_numbers)
    context.log.info("sum of %d numbers = %d", len(raw_numbers), result)
    context.add_output_metadata({"total": result})
    return result


all_assets_job = dg.define_asset_job("all_assets_job", selection="*")

every_minute = dg.ScheduleDefinition(job=all_assets_job, cron_schedule="* * * * *")

defs = dg.Definitions(
    assets=[raw_numbers, total],
    jobs=[all_assets_job],
    schedules=[every_minute],
)
