from elasticsearch import Elasticsearch
client = Elasticsearch(hosts=["http://localhost:9200"], use_ssl=False, verify_certs=False)

print(client.ping())
resp = client.info()
print(resp)
