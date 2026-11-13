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

session.execute("""
    CREATE KEYSPACE IF NOT EXISTS users
    WITH replication = {'class': 'NetworkTopologyStrategy', 'replication_factor': '1'}
""")
session.set_keyspace("users")  # or: session.execute("USE users")
session.execute("CREATE TABLE IF NOT EXISTS users (name text PRIMARY KEY, age int, email text)")
session.execute("INSERT INTO users (name, age, email) VALUES (%s, %s, %s)", ("alice", 30, "alice@example.com"))

for user_row in session.execute("SELECT name, age, email FROM users"):
    print(user_row.name, user_row.age, user_row.email)

# prepared statements use ? placeholders and are the recommended way for repeated queries
by_name = session.prepare("SELECT name, age FROM users WHERE name = ?")
print(session.execute(by_name, ("alice",)).one())
cluster.shutdown()
