# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyspark==4.3.0",
#     "ipython",
# ]
# ///

import os
import sys
from operator import add

from pyspark.sql import SparkSession


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: example_param.py <file>", file=sys.stderr)
        sys.exit(-1)

    spark = (
        SparkSession.builder.appName("PythonWordCount")
        .master(os.getenv("SPARK_MASTER", "local[*]"))
        .getOrCreate()
    )

    lines = spark.read.text(sys.argv[1]).rdd.map(lambda r: r[0])
    counts = lines.flatMap(lambda x: x.split(" ")).map(lambda x: (x, 1)).reduceByKey(add)
    for word, count in counts.collect():
        print(f"{word}: {count}")

    spark.stop()
