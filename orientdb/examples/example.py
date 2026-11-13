# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.32",
# ]
# ///

import os

import requests

URL = os.getenv("ORIENTDB_URL", "http://localhost:2480")
ROOT = ("root", os.getenv("ORIENTDB_ROOT_PASSWORD", "root"))
DB = "animals"
DB_AUTH = ("admin", "admin")  # default user created together with a new database


def sql(command: str):
    resp = requests.post(f"{URL}/command/{DB}/sql", json={"command": command}, auth=DB_AUTH, timeout=30)
    resp.raise_for_status()
    return resp.json()["result"]


# Create the database (graph type, stored on disk) if it does not exist yet
if DB not in requests.get(f"{URL}/listDatabases", timeout=10).json()["databases"]:
    requests.post(f"{URL}/database/{DB}/plocal/graph", auth=ROOT, timeout=60).raise_for_status()

# Create the Vertex Animal and insert a value
sql("CREATE CLASS Animal IF NOT EXISTS EXTENDS V")
sql("INSERT INTO Animal SET name = 'rat', species = 'rodent'")
print(sql("SELECT * FROM Animal"))

# Create the vertex and insert the food values
sql("CREATE CLASS Food IF NOT EXISTS EXTENDS V")
sql("INSERT INTO Food SET name = 'pea', color = 'green'")

# Create the edge class for the Eat action and let the rat eat peas
sql("CREATE CLASS Eat IF NOT EXISTS EXTENDS E")
sql("CREATE EDGE Eat FROM (SELECT FROM Animal WHERE name = 'rat') TO (SELECT FROM Food WHERE name = 'pea')")

# Who eats the peas?
for animal in sql("SELECT EXPAND(in('Eat')) FROM Food WHERE name = 'pea'"):
    print(animal["name"], animal["species"])

# What does each animal eat?
for food in sql("SELECT EXPAND(out('Eat')) FROM Animal"):
    print(food["name"], food["color"])
