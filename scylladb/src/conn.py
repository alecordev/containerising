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

if cluster.is_shard_aware():
    print("connected to a scylla cluster")
print(session.execute("SELECT release_version FROM system.local").one())
cluster.shutdown()
