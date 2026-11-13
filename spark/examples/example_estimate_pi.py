# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyspark==4.3.0",
#     "ipython",
# ]
# ///

import os
import random

from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("EstimatePi")
    .master(os.getenv("SPARK_MASTER", "local[*]"))
    .getOrCreate()
)
sc = spark.sparkContext

NUM_SAMPLES = 1_000_000


def inside(_: int) -> bool:
    x, y = random.random(), random.random()
    return x * x + y * y < 1


count = sc.parallelize(range(NUM_SAMPLES)).filter(inside).count()
print(f"Pi is roughly {4.0 * count / NUM_SAMPLES:f}")
spark.stop()
