import helper

client = helper.connect()


db = client.business

ASingleReview = db.reviews.find_one({})
print("A sample document:")
print(ASingleReview)

result = db.reviews.update_one(
    {"_id": ASingleReview.get("_id")}, {"$inc": {"likes": 1}}
)
print("Number of documents modified : " + str(result.modified_count))

UpdatedDocument = db.reviews.find_one({"_id": ASingleReview.get("_id")})
print("The updated document:")
print(UpdatedDocument)


def delete():
    result = db.restaurants.delete_many({"category": "Bar Food"})
    result = db.restaurants.delete_one({"category": "Bar Food"})
