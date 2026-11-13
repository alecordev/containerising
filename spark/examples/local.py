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

# Usage: python local.py [text-file]  (default: $SPARK_HOME/README.md)
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getenv("SPARK_HOME", "/opt/spark"), "README.md")

spark = SparkSession.builder.appName("LocalLines").master("local[*]").getOrCreate()
sc = spark.sparkContext

txt = sc.textFile(path)
print(txt.count())

python_lines = txt.filter(lambda line: "python" in line.lower())
print(python_lines.count())

spark.stop()
