import pymongo

# from pymongo import MongoClient
#
# # Replace these with your server details
# MONGO_HOST = "XX.XXX.XXX.XXX"
# MONGO_PORT = "27017"
# MONGO_DB = "database"
# MONGO_USER = "admin"
# MONGO_PASS = "pass"
#
# uri = "mongodb://{}:{}@{}:{}/{}?authSource=admin".format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB)
# client = MongoClient(uri)


def connect():
    client = pymongo.MongoClient(host="localhost", port=27017, username="admin", password="admin")
    return client


class MongoConnect:
    def __init__(self):
        self.client = None

    def __enter__(self):
        self.client = pymongo.MongoClient(host="localhost", port=27017, username="admin", password="admin")
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


if __name__ == '__main__':
    conn = connect()
    conn.close()
