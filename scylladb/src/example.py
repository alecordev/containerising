import uuid

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

# Connect to the ScyllaDB cluster
cluster = Cluster(['localhost'])
session = cluster.connect()

# Create a keyspace
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS my_keyspace
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
""")
session.set_keyspace('my_keyspace')

# Create a table for the address book
session.execute("""
    CREATE TABLE IF NOT EXISTS address_book (
        id UUID PRIMARY KEY,
        name TEXT,
        email TEXT,
        phone TEXT
    )
""")

# Insert example entries into the address book
entries = [
    {'id': uuid.uuid4(), 'name': 'John Doe', 'email': 'john.doe@example.com', 'phone': '+1-123-456-7890'},
    {'id': uuid.uuid4(), 'name': 'Jane Smith', 'email': 'jane.smith@example.com', 'phone': '+1-987-654-3210'},
    {'id': uuid.uuid4(), 'name': 'Alice Johnson', 'email': 'alice.johnson@example.com', 'phone': '+1-555-555-5555'}
]

for entry in entries:
    session.execute(
        """
        INSERT INTO address_book (id, name, email, phone)
        VALUES (%s, %s, %s, %s)
        """,
        (entry['id'], entry['name'], entry['email'], entry['phone'])
    )

# Read and print all entries in the address book
rows = session.execute("SELECT * FROM address_book")
for row in rows:
    print(row.id, row.name, row.email, row.phone)

# Close the connection
cluster.shutdown()
