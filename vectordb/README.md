# Vector databases

Four self-contained vector database templates, plus a pointer to the Postgres option already in this repo. Each subdirectory is an independent compose project (own README, `.env.example`, volumes).

| | [qdrant](qdrant) | [weaviate](weaviate) | [milvus](milvus) | [chroma](chroma) | [pgvector](../postgres-pgvector) |
|---|---|---|---|---|---|
| Footprint | Light (single Rust binary) | Medium (Go) | **Heavy** (Milvus + etcd + MinIO) | Light | Light (Postgres) |
| API | REST, gRPC | REST, GraphQL, gRPC | gRPC, REST v2 | REST (Python/JS clients) | SQL |
| Hybrid / keyword search | Yes (sparse vectors) | Yes (BM25 built in) | Yes (sparse / full-text) | Basic | Via Postgres FTS |
| Built-in vectorizer modules | No | Optional modules | No (embedding functions in client) | Embedding functions in client | No |
| Filtering | Rich payload filters | Property filters | Scalar filters | Metadata filters | Any SQL `WHERE` / joins |
| Best for | General production-style workloads, quick start | Hybrid search, multi-tenancy | Very large-scale collections | Prototyping, notebooks, RAG demos | Vectors next to relational data |
| Default port | 6333 / 6334 | 8080 / 50051 | 19530 | 8000 | 5432 |
| Auth in these templates | Optional API key | Anonymous | None | None | Postgres user/password |

**Choosing**: start with Chroma for a notebook prototype, Qdrant for a small service, pgvector if the data already lives in Postgres, Weaviate when you want hybrid search or hosted vectorizers, Milvus when you expect very large collections and are willing to run more components.

## Run

```bash
cd vectordb/<qdrant|weaviate|milvus|chroma>
docker compose up -d --wait
```

Each template can be run one at a time or together (projects are named `qdrant`, `weaviate`, `milvus`, `chroma`), apart from the host-port overlaps noted in each README (Weaviate 8080, Chroma 8000).

All the examples use 4-dimensional toy vectors so they run instantly; real embeddings are typically 384-3072 dimensions.
