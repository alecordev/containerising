# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "neo4j>=6.1,<6.2",
#     "neomodel>=7,<8",
# ]
# ///

import os

from neomodel import (
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    db,
)

user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")
host = os.getenv("NEO4J_URI", "bolt://localhost:7687").split("://", 1)[1]
db.set_connection(url=f"bolt://{user}:{password}@{host}")  # replaces the deprecated config.DATABASE_URL


class Book(StructuredNode):
    title = StringProperty(unique_index=True)
    author = RelationshipTo("Author", "AUTHOR")


class Author(StructuredNode):
    name = StringProperty(unique_index=True)
    books = RelationshipFrom("Book", "AUTHOR")


# Create the unique constraints once, e.g. with: neomodel_install_labels this_module --db <url>
harry_potter = Book(title="Harry potter and the..").save()
rowling = Author(name="J. K. Rowling").save()
harry_potter.author.connect(rowling)
print(harry_potter.author.all())
