# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "scylla-driver>=3.29,<4",
# ]
# ///

import os

from cassandra import ConsistencyLevel
from cassandra.cluster import EXEC_PROFILE_DEFAULT, Cluster, ExecutionProfile
from cassandra.policies import DCAwareRoundRobinPolicy, TokenAwarePolicy
from cassandra.query import tuple_factory

HOSTS = os.getenv("SCYLLA_HOSTS", "localhost").split(",")
PORT = int(os.getenv("SCYLLA_PORT", "9042"))

# Execution profile: token-aware routing, explicit consistency level and timeout
profile = ExecutionProfile(
    load_balancing_policy=TokenAwarePolicy(DCAwareRoundRobinPolicy()),
    consistency_level=ConsistencyLevel.ONE,  # single-node dev cluster
    request_timeout=15,
    row_factory=tuple_factory,
)
cluster = Cluster(HOSTS, port=PORT, execution_profiles={EXEC_PROFILE_DEFAULT: profile})
session = cluster.connect()

print(session.execute("SELECT release_version FROM system.local").one())
cluster.shutdown()
