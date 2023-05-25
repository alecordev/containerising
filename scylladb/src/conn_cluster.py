from cassandra.cluster import Cluster

cluster = Cluster()
session = cluster.connect()

stats = cluster.shard_aware_stats()
if all([v["shards_count"] == v["connected"] for v in stats.values()]):
    print("successfully connected to all shards of all scylla nodes")