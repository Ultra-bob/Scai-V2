import redis
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def create_schema():
    schema = (
        TextField("$.title", as_name="title"),
        TextField("$.content", as_name="content"),
        TextField("$.url", as_name="url")
    )

    index = r.ft("idx:docs")
    index.create_index(
        schema,
        definition=IndexDefinition(prefix=["docs:"], index_type=IndexType.JSON),
    )

create_schema()