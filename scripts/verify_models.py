"""Real smoke run through the same controller used by the browser."""
import asyncio
import argparse
import json
import uuid
from arena.controller import Controller
from arena.contracts import RunRequest

async def run(models,judge=False,preset="smoke"):
    ctl=Controller()
    rid=await ctl.start(RunRequest(model_ids=models,preset=preset,judge=judge,idempotency_key=uuid.uuid4().hex))
    print("Run:",rid,flush=True)
    after=0
    while not ctl.tasks[rid].done():
        for event in ctl.store.events(rid,after):
            after=event["id"]
            if event["kind"]!="prediction":print(event["kind"],event["data"],flush=True)
        await asyncio.sleep(2)
    await ctl.tasks[rid]
    result=ctl.results(rid)
    print(json.dumps({"id":rid,"status":ctl.store.run(rid)["status"],"error":ctl.store.run(rid)["error"],"entrants":[{"name":e["name"],"metrics":{k:e["metrics"][k] for k in ("completed","accuracy","p50_ms","valid","failed")}} for e in result["entrants"]]},indent=2),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("models",nargs="+");p.add_argument("--judge",action="store_true");p.add_argument("--preset",default="smoke",choices=["smoke","demo","full"]);a=p.parse_args()
    asyncio.run(run(a.models,a.judge,a.preset))
