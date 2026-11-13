# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pymongo>=4.19,<5",
#     "mongoengine>=0.29",
#     "python-dotenv>=1.2",
# ]
# ///

import os

from pymongo import MongoClient
from random import randint

client = MongoClient(os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017/?authSource=admin"))

db = client.business

names = [
    "Kitchen",
    "Animal",
    "State",
    "Tastey",
    "Big",
    "City",
    "Fish",
    "Pizza",
    "Goat",
    "Salty",
    "Sandwich",
    "Lazy",
    "Fun",
]
company_type = ["LLC", "Inc", "Company", "Corporation"]
company_cuisine = [
    "Pizza",
    "Bar Food",
    "Fast Food",
    "Italian",
    "Mexican",
    "American",
    "Sushi Bar",
    "Vegetarian",
]
for x in range(1, 501):
    business = {
        "name": names[randint(0, (len(names) - 1))]
        + " "
        + names[randint(0, (len(names) - 1))]
        + " "
        + company_type[randint(0, (len(company_type) - 1))],
        "rating": randint(1, 5),
        "cuisine": company_cuisine[randint(0, (len(company_cuisine) - 1))],
    }
    # Step 3: Insert business object directly into MongoDB via insert_one
    result = db.reviews.insert_one(business)
    # Step 4: Print to the console the ObjectID of the new document
    print("Created {0} of 500 as {1}".format(x, result.inserted_id))
# Step 5: Tell us that you are done
print("finished creating 500 business reviews")

fivestar = db.reviews.find_one({'rating': 5})
print(fivestar)

fivestarcount = db.reviews.find({'rating': 5}).count()
print(fivestarcount)

