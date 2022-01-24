"""
- Write doc
- Read doc
- Update doc
- Search doc
"""

import helper

mongo = helper.connect()
tutorial = mongo.db.tutorial

tutorial1 = {
    "title": "Working With JSON Data in Python",
    "author": "Lucas",
    "contributors": [
        "Aldren",
        "Dan",
        "Joanna"
    ],
    "url": "https://realpython.com/python-json/"
}

result = tutorial.insert_one(tutorial1)
print(result)
print(f"One tutorial: {result.inserted_id}")

tutorial2 = {
    "title": "Python's Requests Library (Guide)",
    "author": "Alex",
    "contributors": [
        "Aldren",
        "Brad",
        "Joanna"
    ],
    "url": "https://realpython.com/python-requests/"
}

tutorial3 = {
    "title": "Object-Oriented Programming (OOP) in Python 3",
    "author": "David",
    "contributors": [
        "Aldren",
        "Joanna",
        "Jacob"
    ],
    "url": "https://realpython.com/python3-object-oriented-programming/"
}

new_result = tutorial.insert_many([tutorial2, tutorial3])

print(f"Multiple tutorials: {new_result.inserted_ids}")

import pprint

for doc in tutorial.find():
    pprint.pprint(doc)

jon_tutorial = tutorial.find_one({"author": "Jon"})

pprint.pprint(jon_tutorial)

mongo.close()
