
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

# Create a table
session.execute("""
    CREATE TABLE IF NOT EXISTS my_table (
        id UUID PRIMARY KEY,
        name TEXT,
        age INT
    )
""")

# Insert a record
session.execute("""
    INSERT INTO my_table (id, name, age)
    VALUES (uuid(), 'John Doe', 25)
""")

# Read records
rows = session.execute("SELECT * FROM my_table")
for row in rows:
    print(row.id, row.name, row.age)

# Update a record
session.execute("""
    UPDATE my_table
    SET age = 30
    WHERE id = ?
""", ('id_value',))

# Delete a record
session.execute("""
    DELETE FROM my_table
    WHERE id = ?
""", ('id_value',))

# Drop the table
session.execute("DROP TABLE IF EXISTS my_table")

# Drop the keyspace
session.execute("DROP KEYSPACE IF EXISTS my_keyspace")

# Close the connection
cluster.shutdown()