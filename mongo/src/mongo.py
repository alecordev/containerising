# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pymongo>=4.19,<5",
# ]
# ///

import os
import uuid

import pymongo

client = pymongo.MongoClient(
    os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017/?authSource=admin")
)

print(list(client.list_databases()))
collection = client["database"]["collection"]
print(collection)

items = [{"id": str(uuid.uuid4()), "number": 42, "order": i} for i in range(2)]

collection.insert_many(items)
collection.insert_one(
    {"id": str(uuid.uuid4()), "number": 42, "order": 99, "name": "Ale"}
)

item_details = collection.find()
for item in item_details:
    print(item)
    print(item["number"], item.get("order"))

print("Filtering")
item_details = collection.find({"order": 1})
for item in item_details:
    print(item["number"], item.get("order"))

print("Create index")
category_index = collection.create_index("order")

q = {"order": 5}
print(collection.delete_one(q))

query = {"name": {"$regex": "^A"}}
print([item for item in collection.find(query)])
d = collection.delete_many(query)
print(d.deleted_count, " document(s) deleted")
