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

session.execute("""
    CREATE TABLE IF NOT EXISTS address_book (
        id UUID PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT
    )
""")

entries = [
    (uuid.uuid4(), "John Doe", "john.doe@example.com", "+1-123-456-7890"),
    (uuid.uuid4(), "Jane Smith", "jane.smith@example.com", "+1-987-654-3210"),
    (uuid.uuid4(), "Alice Johnson", "alice.johnson@example.com", "+1-555-555-5555"),
]
insert = session.prepare("INSERT INTO address_book (id, name, email, phone) VALUES (?, ?, ?, ?)")
for entry in entries:
    session.execute(insert, entry)

for row in session.execute("SELECT * FROM address_book"):
    print(row.id, row.name, row.email, row.phone)

cluster.shutdown()
