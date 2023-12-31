import redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

r = redis.Redis(host="data-db", port=6379, db=0, decode_responses=True)

def create_schema():
    schema = (
        TextField("$.title", as_name="title"),
        TextField("$.content", as_name="content"),
        TextField("$.description", as_name="description"),
        TextField("$.url", as_name="url"),
        VectorField(
        "$.description_embeddings",
            "FLAT",
            {
                "TYPE": "FLOAT32",
                "DIM": 1024, # cohere vector dimension
                "DISTANCE_METRIC": "IP",
            },
            as_name="vector",
        ),
    )

    index = r.ft("idx:docs")
    index.create_index(
        schema,
        definition=IndexDefinition(prefix=["docs:"], index_type=IndexType.JSON),
    )

create_schema()