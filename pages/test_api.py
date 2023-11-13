from pynng import Pair1
from json import dumps, loads

with Pair1(dial="tcp://localhost:23214", polyamorous=True) as s:

    s.send(dumps(["search", "The 300i"]).encode())

    print(loads(s.recv_msg().bytes))