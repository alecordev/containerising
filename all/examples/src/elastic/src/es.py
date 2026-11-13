# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "elasticsearch[async]>=9.5,<10",
#     "python-dotenv>=1.2",
# ]
# ///

import os

from elasticsearch import Elasticsearch

client = Elasticsearch(os.getenv("ELASTICSEARCH_URL", "http://localhost:9200"))

print(client.ping())
print(client.info())
