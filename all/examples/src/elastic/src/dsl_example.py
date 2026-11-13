# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "elasticsearch[async]>=9.5,<10",
#     "python-dotenv>=1.2",
# ]
# ///

from datetime import datetime
import os

from elasticsearch.dsl import Date, Document, Integer, Keyword, Text, connections

# Define a default Elasticsearch client
connections.create_connection(hosts=[os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")])


class Article(Document):
    title = Text(analyzer="snowball", fields={"raw": Keyword()})
    body = Text(analyzer="snowball")
    tags = Keyword()
    published_from = Date()
    lines = Integer()

    class Index:
        name = "blog"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    def save(self, **kwargs):
        self.lines = len(self.body.split())
        return super(Article, self).save(**kwargs)

    def is_published(self):
        return datetime.now() > self.published_from


# create the mappings in elasticsearch
Article.init()

# create and save and article
article = Article(meta={"id": 42}, title="Hello world!", tags=["test"])
article.body = """ looong text """
article.published_from = datetime.now()
article.save()

article = Article.get(id=42)
print(article.is_published())

# Display cluster health
print(connections.get_connection().cluster.health())
