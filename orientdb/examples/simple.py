import pyorient

username = "root"
password = "root"

client = pyorient.OrientDB("localhost", 2424)
session_id = client.connect(username, password)

print("SessionID=", session_id)
db_name = "GratefulDeadConcerts"

if client.db_exists(db_name, pyorient.STORAGE_TYPE_MEMORY):
    print("Database", db_name, "exists")
    client.db_open(db_name, username, password)
else:
    print("Database", db_name, "doesn't exist")
