from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

# Connect to the ScyllaDB cluster
cluster = Cluster(['localhost'])
session = cluster.connect()

session.set_keyspace('users')
# or you can do this instead
# session.execute('USE users')

rows = session.execute('SELECT name, age, email FROM users')
for user_row in rows:
    print(user_row.name, user_row.age, user_row.email)