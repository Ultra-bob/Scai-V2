from pynng import Pair1
import trio
from redis.commands.search.query import Query
from redis import Redis
from json import loads, dumps
import numpy as np
from cohere import Client
from dotenv import load_dotenv
from os import getenv

print(load_dotenv("/run/secrets/dotenv", verbose=True))

co = Client()

db = Redis(host="redis-stack", port=6379, db=0, decode_responses=True)
index = db.ft("idx:docs")

dumpb = lambda data: dumps(data).encode()

PORT = "8000"

async def polyamorous_send_and_recv():
    address = 'tcp://0.0.0.0:' + PORT
    with Pair1(listen=address, polyamorous=True) as s:
        while True:
            msg = await s.arecv_msg()
            content = loads(msg.bytes)
            match content[0], content[1:]:
                case "get", [title]:
                    results = index.search(Query(f'@title:"{title}"').return_field("content")).docs
                    if len(results) == 0:
                        await msg.pipe.asend(dumpb({"status": "error", "content": "Page not found!"}))
                    else:
                        await msg.pipe.asend(dumpb({"status": "ok", "content": results[0].content}))
                case "search", [query]:
                    query_emb = co.embed([query], input_type="search_query", model="embed-english-v3.0").embeddings[0]

                    results = index.search(Query('(*)=>[KNN 5 @vector $query_vector AS vector_score]')
                    .sort_by('vector_score')
                    .dialect(2), {'query_vector': np.array(query_emb, dtype=np.float32).tobytes()} ).docs

                    if results:
                        await msg.pipe.asend(dumpb({"status": "ok", "content": [r.json for r in results]}))
                    else:
                        await msg.pipe.asend(dumpb({"status": "error", "content": "No results!"}))




        

trio.run(polyamorous_send_and_recv)