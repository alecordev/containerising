# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyspark==4.3.0",
#     "ipython",
# ]
# ///

import os

from pyspark.sql import SparkSession

# Submit to the standalone cluster from docker-compose.yml.
# Run inside the cluster:  spark-submit --master spark://spark-master:7077 using_cluster.py
# Run from the host:       SPARK_MASTER=spark://localhost:7077 python using_cluster.py
spark = (
    SparkSession.builder.appName("UsingCluster")
    .master(os.getenv("SPARK_MASTER", "spark://spark-master:7077"))
    # .config("spark.authenticate", "true")
    # .config("spark.authenticate.secret", "secret-key")
    .getOrCreate()
)
sc = spark.sparkContext

rdd = sc.parallelize(range(10000), 2)
odds = rdd.filter(lambda x: x % 2 != 0)
print(odds.take(5))

spark.stop()
