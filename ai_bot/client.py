from pynng import Pair1
from json import loads, dumps

dumpb = lambda data: dumps(data).encode()

with Pair1(dial="tcp://localhost:23215") as s:
    s.send(dumpb({"query": "What shield generator does the 325i have?", "id": "random_data"}))
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