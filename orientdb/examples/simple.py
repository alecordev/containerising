# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.32",
# ]
# ///

import os

import requests

URL = os.getenv("ORIENTDB_URL", "http://localhost:2480")
ROOT_PASSWORD = os.getenv("ORIENTDB_ROOT_PASSWORD", "root")
DB_NAME = "GratefulDeadConcerts"

resp = requests.get(f"{URL}/listDatabases", timeout=10)
resp.raise_for_status()
databases = resp.json()["databases"]
print("Databases:", databases)

if DB_NAME in databases:
    print("Database", DB_NAME, "exists")
else:
    print("Database", DB_NAME, "doesn't exist")
