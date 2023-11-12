from pynng import Pair1
from json import dumps

with Pair1(dial="tcp://127.0.0.1:23214",polyamorous=True) as s:

    s.send(dumps(["search", "The 300i"]).encode())

    print(s.recv_msg().bytes)