# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pymongo>=4.19,<5",
#     "mongoengine>=0.29",
#     "python-dotenv>=1.2",
# ]
# ///

import os

import pymongo

mongo = pymongo.MongoClient(os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017/?authSource=admin"))
print(mongo)
print(mongo.admin.command("ping"))
print(mongo.admin.command("serverStatus")["version"])
mongo.close()
