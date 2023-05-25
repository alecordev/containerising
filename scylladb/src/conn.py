from cassandra.cluster import Cluster

cluster = Cluster()
session = cluster.connect()

if cluster.is_shard_aware():
    print("connected to a scylla cluster")