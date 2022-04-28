import pyspark
from pyspark import SparkContext

conf = pyspark.SparkConf()
conf.setMaster('spark://localhost:7077')
# conf.set('spark.authenticate', True)
# conf.set('spark.authenticate.secret', 'secret-key')
sc = SparkContext(conf=conf)

big_list = range(10000)
rdd = sc.parallelize(big_list, 2)
odds = rdd.filter(lambda x: x % 2 != 0)
odds.take(5)
