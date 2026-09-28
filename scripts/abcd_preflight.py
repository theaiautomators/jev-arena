"""GPU-serialized development-only ABCD capacity preflight, resumable by record."""
import asyncio
import dataclasses
import json
import time
from pathlib import Path
from filelock import FileLock, Timeout
from arena import adapters
from arena.adapters import Adapter
from arena.config import ROOT,DATA,write_json,digest
from arena.contracts import Case

FOLDER=DATA/"abcd-v1"
MODELS=["jev","winnow","decider","nimble","qwen"]
CONTEXTS={"jev":32000,"winnow":65536,"decider":32768,"nimble":8192,"qwen":32768}
BASE_LEDGER=DATA/"runs/20260927-205440-6350b9"
CAP=6.0

def budget():
    paths=[BASE_LEDGER/"workers/jev/cost-ledger.json",BASE_LEDGER/"followups/workers/jev/cost-ledger.json"]+list(FOLDER.rglob("cost-ledger.json"))
    records=[json.loads(p.read_text(encoding="utf-8")) for p in paths]
    return {"combined_cap_usd":CAP,"actual_usd":sum(x["actual_usd"] for x in records),"reserved_usd":sum(x["reserved_usd"] for x in records),"ledgers":len(paths)}

def progress(stage,**kwargs):
    write_json(FOLDER/"progress.json",{"stage":stage,"updated":time.time(),"test_predictions_started":False,**kwargs})

def configured_adapter(mid,folder,cancel):
    adapters.IMAGE="jev-arena-abcd-worker:0.1"
    adapters.IMAGES={"winnow":"jev-arena-abcd-winnow:0.1"}
    a=Adapter(mid,folder,cancel)
    a.entrant=dataclasses.replace(a.entrant,context=CONTEXTS[mid])
    return a

async def predict(a,c):
    ledger=budget()
    if ledger["reserved_usd"]>CAP:raise RuntimeError("Combined authorized cap exhausted")
    return await a.predict(c,cap=a.reserved+CAP-ledger["reserved_usd"])

async def main():
    cases=[Case.model_validate_json(line) for line in (FOLDER/"dev-cases.jsonl").read_text(encoding="utf-8").splitlines()]
    selected=[]
    for task,condition in (("action","retrieved_policy"),("action","full_handbook"),("route","full_handbook")):
        selected.append(max((c for c in cases if c.family==task and c.provenance["condition"]==condition),key=lambda c:len(c.state)))
    for length in (4096,8192,16384,28672):
        selected.append(next(c for c in cases if c.family=="synthetic_action" and c.provenance["base"]==0 and c.provenance["target_state_tokens_qwen"]==length and c.provenance["evidence_position"]=="early"))
    selected_ids=[c.id for c in selected]
    folder=FOLDER/"runs/abcd-dev-preflight-v2"
    folder.mkdir(parents=True,exist_ok=True)
    plan={"case_ids":selected_ids,"models":MODELS,"contexts":CONTEXTS,"source_sha256":digest((FOLDER/"dev-cases.jsonl").read_bytes()),"scope":"Development-only load, token/capacity, no-truncation, latency, VRAM and cleanup checks. No ABCD test predictions."}
    if (folder/"plan.json").exists():assert json.loads((folder/"plan.json").read_text(encoding="utf-8"))==plan
    else:write_json(folder/"plan.json",plan)
    lock=FileLock(DATA/"gpu.lock")
    while True:
        try:lock.acquire(timeout=0);break
        except Timeout:progress("preflight_waiting_for_gpu");await asyncio.sleep(30)
    try:
        for mid in MODELS:
            work=folder/"workers"/mid;work.mkdir(parents=True,exist_ok=True)
            journal=work/"predictions.jsonl"
            rows=[json.loads(x) for x in journal.read_text(encoding="utf-8").splitlines()] if journal.exists() else []
            done={x["case_id"] for x in rows}
            if done==set(selected_ids) and (work/"cleanup.json").exists():continue
            cancel=asyncio.Event();a=configured_adapter(mid,work,cancel)
            progress("preflight_loading",model=mid,completed=len(done),total=len(selected))
            try:
                await a.load();write_json(work/"metadata.json",a.meta)
                for c in selected:
                    if c.id in done:continue
                    progress("preflight_evaluating",model=mid,case_id=c.id,completed=len(done),total=len(selected))
                    p=await predict(a,c)
                    with journal.open("a",encoding="utf-8") as f:f.write(json.dumps({"case_id":c.id,"prediction":p.model_dump(),"recorded":time.time()},ensure_ascii=False)+"\n");f.flush()
                    done.add(c.id)
                    if p.status in ("timeout","transport_error"):raise RuntimeError(f"{mid}: {p.status}: {p.error}")
            finally:
                clean=await a.unload();write_json(work/"cleanup.json",clean)
                if not clean.get("memory_within_baseline",True):raise RuntimeError("GPU cleanup exceeded baseline")
        progress("preflight_complete",models=MODELS,budget=budget())
        write_json(folder/"complete.json",{"at":time.time(),"models":MODELS,"probes_per_model":len(selected),"budget":budget()})
    except BaseException as e:
        progress("preflight_needs_recovery",error=str(e));raise
    finally:lock.release()

if __name__=="__main__":asyncio.run(main())
