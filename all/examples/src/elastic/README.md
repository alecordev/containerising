# Elasticsearch with Python

Targets the 9.x client against the single-node stack in `../../../docker-compose.yml`
(`ELASTICSEARCH_URL`, default `http://localhost:9200`; security is disabled for local development).
The DSL helpers now ship inside the client: `from elasticsearch.dsl import ...` (the separate `elasticsearch-dsl` package is no longer needed).

## Resources

- https://elasticsearch-py.readthedocs.io/en/stable/
- https://elasticsearch-py.readthedocs.io/en/stable/esql.html
