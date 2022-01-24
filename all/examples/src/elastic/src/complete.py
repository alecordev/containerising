import datetime
import uuid

import elasticsearch
from elasticsearch import helpers
from elasticsearch import Elasticsearch

client = Elasticsearch(
    hosts=["http://localhost:9200"], use_ssl=False, verify_certs=False
)

print(client.ping())
resp = client.info()
print(resp)

# Create index
index_name = "companies"
mapping = {
    "settings": {"number_of_shards": "20", "number_of_replicas": "2"},
    "mappings": {
        "properties": {
            "article_id": {"type": "keyword"},
            "article_pubdate": {"type": "date"},
            "company_types": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "count": {"type": "long"},
            "entity_type": {"type": "keyword"},
            "is_negative": {"type": "boolean"},
            "is_positive": {"type": "boolean"},
            "name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "original": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "sentences": {"type": "long"},
            "sentiment": {"type": "keyword"},
            "created": {"type": "date"},
        }
    },
}
response = client.indices.create(index=index_name, body=mapping, ignore=400)
print(response)

if "acknowledged" in response:
    if response["acknowledged"]:
        print(f"Index created successfully: {response['index']}")

    elif "error" in response:
        print(f"Error creating index: {response['error']['root_cause']}")
        print(f"Error Type: {response['error']['type']}")

mapping2 = {
    "settings": {
        "refresh_interval": "300s",
        "number_of_shards": 5,
        "number_of_replicas": 3,
    },
    "mappings": {
        "properties": {
            "entities": {"type": "flattened"},
            "body": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "id": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "language": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "meta": {"type": "flattened", "ignore_above": 256},
            "provider_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "publication_time": {"type": "date"},
            "service_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "source_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "stamp_created": {"type": "date"},
            "links": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "title": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
        }
    },
}

response = client.indices.create(index="new", body=mapping2, ignore=400)
print(response)

if "acknowledged" in response:
    if response["acknowledged"]:
        print(f"Index created successfully: {response['index']}")

    elif "error" in response:
        print(f"Error creating index: {response['error']['root_cause']}")
        print(f"Error Type: {response['error']['type']}")


documents = [
    {
        "body": "This is the body",
        "id": uuid.uuid4(),
        "language": "ES",
        "publication_time": datetime.datetime.utcnow(),
        "stamp_created": datetime.datetime.utcnow(),
        "title": "Title",
    },
]
resp = list(helpers.parallel_bulk(client, documents, index="new"))
print(resp)
