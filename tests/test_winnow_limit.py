import asyncio
import json
from arena.adapters import Adapter
from arena.contracts import Case,Question

class Sink:
    def __init__(self):self.sent=[]
    def write(self,data):self.sent.append(data)
    async def drain(self):pass

async def probe(tmp_path,n):
    labels=[str(i) for i in range(n)]
    c=Case(id="boundary",cluster="boundary",pack="test",family="test",state="Pick zero",question=Question(id="q",text="Choose",kind="choice",labels=labels),gold="0")
    a=Adapter("winnow",tmp_path,asyncio.Event())
    sink=Sink()
    a.proc=type("Proc",(),{"stdin":sink})()
    async def reply(timeout):return json.dumps({"selected":"0","probabilities":{k:float(k=="0") for k in labels},"probability_source":"native"}).encode()
    a._line=reply
    return await a.predict(c),sink.sent

def test_native_limit_rejected_before_worker_request(tmp_path):
    prediction,sent=asyncio.run(probe(tmp_path,65))
    assert prediction.status=="unsupported" and not sent

def test_native_limit_boundary_reaches_worker(tmp_path):
    prediction,sent=asyncio.run(probe(tmp_path,64))
    assert prediction.status=="ok" and len(sent)==1
