# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "scylla-driver>=3.29,<4",
# ]
# ///

import os
import uuid

from cassandra.cluster import Cluster

HOSTS = os.getenv("SCYLLA_HOSTS", "localhost").split(",")
PORT = int(os.getenv("SCYLLA_PORT", "9042"))

cluster = Cluster(HOSTS, port=PORT)
session = cluster.connect()

session.execute("""
    CREATE KEYSPACE IF NOT EXISTS my_keyspace
    WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': '1'}
""")
session.set_keyspace("my_keyspace")
session.execute("CREATE TABLE IF NOT EXISTS my_table (id UUID PRIMARY KEY, name TEXT, age INT)")

# Create
record_id = uuid.uuid4()
session.execute("INSERT INTO my_table (id, name, age) VALUES (%s, %s, %s)", (record_id, "John Doe", 25))

# Read
for row in session.execute("SELECT * FROM my_table"):
    print(row.id, row.name, row.age)

# Update
session.execute("UPDATE my_table SET age = %s WHERE id = %s", (30, record_id))

# Delete
session.execute("DELETE FROM my_table WHERE id = %s", (record_id,))

# Cleanup
session.execute("DROP TABLE IF EXISTS my_table")
session.execute("DROP KEYSPACE IF EXISTS my_keyspace")

cluster.shutdown()
