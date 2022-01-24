from elasticsearch import Elasticsearch

es_client = Elasticsearch()

configurations = {
    "settings": {
        "index": {"number_of_replicas": 2},
        "analysis": {
            "filter": {
                "ngram_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 15,
                },
            },
            "analyzer": {
                "ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "ngram_filter"],
                },
            },
        },
    },
    "mappings": {
        "properties": {
            "id": {"type": "long"},
            "name": {
                "type": "text",
                "analyzer": "standard",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "ngrams": {"type": "text", "analyzer": "ngram_analyzer"},
                },
            },
            "brand": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"},
                },
            },
            "price": {"type": "float"},
            "attributes": {
                "type": "nested",
                "properties": {
                    "attribute_name": {"type": "text"},
                    "attribute_value": {"type": "text"},
                },
            },
        }
    },
}

resp = es_client.indices.create(index="laptops-demo", body=configurations, ignore=400)
print(resp)

resp = es_client.indices.put_alias(index="laptops-demo", name="laptops")
print(resp)

resp = es_client.indices.get_alias(index="laptops-demo")
print(resp)

resp = es_client.indices.get_alias(
    index="laptops-demo", allow_no_indices=True, ignore_unavailable=True
)
print(resp)

# resp = es_client.indices.delete(index="laptops-demo", ignore=404)
# print(resp)
#
# resp = es_client.indices.delete_alias(index="laptops-demo", name="laptops")
# print(resp)

doc = {
    "id": 1,
    "name": "HP EliteBook 820 G2",
    "brand": "HP",
    "price": 38842.00,
    "attributes": [
        {"attribute_name": "cpu", "attribute_value": "Intel Core i7-5500U"},
        {"attribute_name": "memory", "attribute_value": "8GB"},
        {"attribute_name": "storage", "attribute_value": "256GB"},
    ],
}
resp = es_client.index(index="laptops-demo", id=1, body=doc)
print("Write document with specific id")
print(resp)

resp = es_client.get(index="laptops-demo", id=1)
print("Get document by id")
print(resp)

search_query = {
    "query": {
        "match": {
        "name": "HP"
        }
    }
}
resp = es_client.search(index="laptops-demo", body=search_query)
print("Search name HP")
print(resp)

search_query = {
    "query": {
        "match": {
        "name.ngrams": "HP"
        }
    }
}
resp = es_client.search(index="laptops-demo", body=search_query)
print("Search name.ngrams HP")
print(resp)
