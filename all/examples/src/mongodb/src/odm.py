# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pymongo>=4.19,<5",
#     "mongoengine>=0.29",
#     "python-dotenv>=1.2",
# ]
# ///

import os

from mongoengine import Document, ListField, StringField, URLField, connect

# connect(db="tutorials", host="localhost", port=27017, username="admin", password="admin")
connect(db="tutorial", host=os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017/?authSource=admin"))


class Tutorial(Document):
    title = StringField(required=True, max_length=70)
    author = StringField(required=True, max_length=20)
    contributors = ListField(StringField(max_length=20))
    url = URLField(required=True)


tutorial1 = Tutorial(
    title="Beautiful Soup: Build a Web Scraper With Python",
    author="Martin",
    contributors=["Aldren", "Geir Arne", "Jaya", "Joanna", "Mike"],
    url="https://realpython.com/beautiful-soup-web-scraper-python/",
)

tutorial1.save()  # Insert the new tutorial

tutorial2 = Tutorial()
tutorial2.title = "something"
tutorial2.author = "Alex"
tutorial2.contributors = ["Aldren", "Jon", "Joanna"]
tutorial2.url = "https://realpython.com/convert-python-string-to-int/"
tutorial2.save()

for doc in Tutorial.objects:
    print(doc.title)


for doc in Tutorial.objects(author="Alex"):
    print(doc.title)
