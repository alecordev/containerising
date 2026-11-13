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

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017/?authSource=admin")


def connect():
    return pymongo.MongoClient(MONGO_URI)


class MongoConnect:
    def __init__(self):
        self.client = None

    def __enter__(self):
        self.client = connect()
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


if __name__ == "__main__":
    conn = connect()
    print(conn.server_info()["version"])
    conn.close()
