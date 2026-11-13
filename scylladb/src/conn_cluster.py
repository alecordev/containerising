# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "scylla-driver>=3.29,<4",
# ]
# ///

import os

from cassandra.cluster import Cluster

HOSTS = os.getenv("SCYLLA_HOSTS", "localhost").split(",")
PORT = int(os.getenv("SCYLLA_PORT", "9042"))

cluster = Cluster(HOSTS, port=PORT)
session = cluster.connect()

stats = cluster.shard_aware_stats()
if all(v["shards_count"] == v["connected"] for v in stats.values()):
    print("successfully connected to all shards of all scylla nodes")
cluster.shutdown()
