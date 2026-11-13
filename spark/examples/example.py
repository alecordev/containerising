# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyspark==4.3.0",
#     "ipython",
# ]
# ///

import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# Usage: python example.py [text-file]   (default: $SPARK_HOME/README.md, i.e. /opt/spark/README.md in the image)
log_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getenv("SPARK_HOME", "/opt/spark"), "README.md")

spark = (
    SparkSession.builder.appName("SimpleApp")
    .master(os.getenv("SPARK_MASTER", "local[*]"))
    .getOrCreate()
)
log_data = spark.read.text(log_file).cache()

num_as = log_data.filter(F.col("value").contains("a")).count()
num_bs = log_data.filter(F.col("value").contains("b")).count()

print(f"Lines with a: {num_as}, lines with b: {num_bs}")

spark.stop()
