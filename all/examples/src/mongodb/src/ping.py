import pymongo

mongo = pymongo.MongoClient(host="localhost", port=27017, username="admin", password="admin")
db = mongo.admin
print(mongo)
# print(mongo.get_default_database())
print(mongo.nodes)
serverStatusResult = db.command("serverStatus")
print(serverStatusResult)
mongo.close()
