from pynng import Pair1
from json import loads, dumps
from secrets import token_urlsafe
from time import time

dumpb = lambda data: dumps(data).encode()

with Pair1(dial="tcp://localhost:23215") as s:
    s.send(dumpb({"query": "Compare the p52 and 72", "id": token_urlsafe(16), "timestamp": time()}))
    #print("Sent")
    while True:
        #print("Waiting...")
        data = loads(s.recv_msg().bytes)
        #print(data)
        match data:
            case {"update": update}:
                print(f"{update}...")
            case {"result": result}:
                print()
                print(result)
                break
            case {"error": error}:
                print(error)
                break