"""Freeze and run the separately authorized ABCD assessment; no test tuning."""
import argparse
import asyncio
import json
import os
import time
from collections import defaultdict,Counter
from dataclasses import asdict
from pathlib import Path
from filelock import FileLock,Timeout
from arena.abcd import PolicyRetriever,stable
from arena.config import ROOT,DATA,digest,write_json
from arena.contracts import Case
from arena.registry import REGISTRY
from arena.hardware import command
from scripts.abcd_preflight import configured_adapter,predict,budget,MODELS,CONTEXTS

FOLDER=DATA/"abcd-v1"
RUN=FOLDER/"runs/abcd-test-v1"
PREFLIGHT=FOLDER/"runs/abcd-dev-preflight-v2"
FILES=["arena/abcd.py","arena/adapters.py","arena/config.py","arena/contracts.py","arena/registry.py","arena/scoring.py","arena/wire.py","workers/abcd_runner.py","workers/abcd_winnow_runner.py","scripts/abcd_preflight.py","scripts/run_abcd_assessment.py","docs/ABCD-PROTOCOL.md"]

def progress(stage,**fields):
    write_json(FOLDER/"progress.json",{"stage":stage,"updated":time.time(),"test_predictions_started":True,**fields})
    print(json.dumps({"stage":stage,**fields}),flush=True)

def fingerprint():
    images={}
    for name in ("jev-arena-abcd-worker:0.1","jev-arena-abcd-winnow:0.1"):
        data=command(["docker","image","inspect",name,"--format","{{.Id}}"])
        if not data["ok"]:raise RuntimeError("Missing ABCD image")
        images[name]=data["text"].strip()
    return {"files":{name:digest((ROOT/name).read_bytes()) for name in FILES},"images":images,"weights":{mid:digest((DATA/"models"/mid/"arena-manifest.json").read_bytes()) for mid in MODELS if mid!="jev"},"test_cases":digest((FOLDER/"test-cases.jsonl").read_bytes()),"dev_cases":digest((FOLDER/"dev-cases.jsonl").read_bytes()),"policy_sections":digest((FOLDER/"policy-sections.json").read_bytes()),"source_manifest":digest((FOLDER/"source-manifest.json").read_bytes())}

def audit_ids(cases):
    natural=defaultdict(list);stress=defaultdict(list)
    for c in cases:
        p=c.provenance
        if c.pack=="ABCD next action":natural[(c.family,p["condition"])].append(c)
        else:stress[(p["target_state_tokens_qwen"],p["evidence_position"])].append(c)
    ids=[]
    for key,group in sorted(natural.items()):ids += [c.id for c in sorted(group,key=lambda c:stable("audit",c.id))[:16]]
    for key,group in sorted(stress.items()):ids.append(min(group,key=lambda c:stable("audit",c.id)).id)
    assert len(ids)==len(set(ids))==76
    return ids

def freeze(cases):
    fp=fingerprint()
    path=FOLDER/"test-freeze.json"
    if path.exists():
        frozen=json.loads(path.read_text(encoding="utf-8"));assert frozen["fingerprint"]==fp,"Inference, prompt, protocol or runtime drift; refusing mixed evidence"
        return frozen
    assert (PREFLIGHT/"complete.json").exists(),"Development capacity checks have not completed"
    plan=json.loads((PREFLIGHT/"plan.json").read_text(encoding="utf-8"))
    assert plan["source_sha256"]==fp["dev_cases"]
    dev_lookup={c.id:c for c in [Case.model_validate_json(line) for line in (FOLDER/"dev-cases.jsonl").read_text(encoding="utf-8").splitlines()]}
    for mid in MODELS:
        work=PREFLIGHT/"workers"/mid
        rows=[json.loads(line) for line in (work/"predictions.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(rows)==len({r["case_id"] for r in rows})==7
        assert {r["case_id"] for r in rows}==set(plan["case_ids"])
        assert all(r["prediction"]["input_hash"]==digest(dev_lookup[r["case_id"]].candidate()) for r in rows)
        assert all(r["prediction"]["status"] in ("ok","invalid","unsupported") for r in rows)
        assert all(r["prediction"]["input_tokens"] is not None for r in rows),"Exact input token reporting is missing"
        assert any(r["prediction"]["status"]=="ok" for r in rows),"No working development response"
        assert json.loads((work/"cleanup.json").read_text(encoding="utf-8")).get("memory_within_baseline",True)
    assert len(cases)==2544 and len({c.id for c in cases})==2544
    assert len({c.cluster for c in cases if c.pack=="ABCD next action"})==300
    frozen={"id":"abcd-test-v1","created":time.time(),"fingerprint":fp,"models":[{**asdict(REGISTRY[mid]),"context":CONTEXTS[mid]} for mid in MODELS],"order":sorted(MODELS,key=lambda mid:stable("model-order",mid)),"case_order":[c.id for c in sorted(cases,key=lambda c:stable("case-order",c.id))],"cases_per_model":2544,"natural_per_model":2400,"synthetic_per_model":144,"audit_case_ids":audit_ids(cases),"budget_at_freeze":budget(),"primary_scoring":"Strict valid-label and selected-label reference agreement on supported attempts; availability and all-planned correct-label yield separately. Natural route/conditional action/combined remain separate from synthetic stress.","judge":{"requested_model":"gpt-6-astra","transport":"Codex CLI","max_batch_answers":8,"rubric":"arena-rubric-v2","blind":True},"preflight":"abcd-dev-preflight-v2"}
    RUN.mkdir(parents=True,exist_ok=True)
    snapshot=RUN/"source";snapshot.mkdir(exist_ok=True)
    for name in FILES:
        target=snapshot/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
    write_json(path,frozen)
    write_json(RUN/"manifest.json",frozen)
    return frozen

async def main(wait=False):
    while not (PREFLIGHT/"complete.json").exists():
        if not wait:raise RuntimeError("Development preflight incomplete")
        write_json(FOLDER/"test-queue.json",{"stage":"waiting_for_preflight","updated":time.time(),"test_predictions_started":False})
        await asyncio.sleep(30)
    cases=[Case.model_validate_json(line) for line in (FOLDER/"test-cases.jsonl").read_text(encoding="utf-8").splitlines()]
    frozen=freeze(cases);lookup={c.id:c for c in cases}
    cases=[lookup[cid] for cid in frozen["case_order"]]
    dev=[Case.model_validate_json(line) for line in (FOLDER/"dev-cases.jsonl").read_text(encoding="utf-8").splitlines()]
    warmups=sorted((c for c in dev if c.provenance.get("condition")=="retrieved_policy"),key=lambda c:stable("warmup",c.id))[:2]
    sections=json.loads((FOLDER/"policy-sections.json").read_text(encoding="utf-8"));retriever=PolicyRetriever(sections)
    lock=FileLock(DATA/"gpu.lock")
    while True:
        try:lock.acquire(timeout=0);break
        except Timeout:progress("waiting_for_gpu_lease");await asyncio.sleep(30)
    started=time.time();write_json(RUN/"last-session.json",{"started":started,"fingerprint":frozen["fingerprint"]})
    try:
        for mid in frozen["order"]:
            assert fingerprint()==frozen["fingerprint"],"Runtime changed after freeze"
            work=RUN/"workers"/mid;work.mkdir(parents=True,exist_ok=True)
            journal=work/"predictions.jsonl"
            rows=[json.loads(x) for x in journal.read_text(encoding="utf-8").splitlines()] if journal.exists() else []
            done={x["prediction"]["case_id"] for x in rows}
            assert len(done)==len(rows)
            for row in rows:assert row["prediction"]["input_hash"]==digest(lookup[row["prediction"]["case_id"]].candidate())
            if len(done)==len(cases) and (work/"cleanup.json").exists():continue
            a=configured_adapter(mid,work,asyncio.Event())
            progress("loading",model=mid,completed=len(done),total=len(cases))
            try:
                await a.load();write_json(work/"metadata.json",a.meta)
                for idx,c in enumerate(warmups):
                    p=await predict(a,c)
                    write_json(work/("warmup-"+str(time.time_ns())+".json"),p.model_dump())
                    if p.status not in ("ok","invalid"):raise RuntimeError("Development warmup failed: "+str(p.error))
                for c in cases:
                    if c.id in done:continue
                    start=time.perf_counter();retrieval_ms=0.
                    if c.provenance.get("condition")=="retrieved_policy":
                        history=c.state.rsplit("\n\nOBSERVED CONVERSATION SO FAR\n",1)[1]
                        chosen=retriever.retrieve(history)
                        assert [s["id"] for s in chosen]==c.provenance["retrieved_sections"]
                        retrieval_ms=(time.perf_counter()-start)*1000
                    p=await predict(a,c)
                    row={"prediction":p.model_dump(),"recorded":time.time(),"retrieval_ms":retrieval_ms,"pipeline_ms":(time.perf_counter()-start)*1000}
                    with journal.open("a",encoding="utf-8") as f:
                        f.write(json.dumps(row,ensure_ascii=False)+"\n");f.flush();os.fsync(f.fileno())
                    done.add(c.id)
                    if len(done)%20==0:progress("evaluating",model=mid,completed=len(done),total=len(cases),budget=budget())
                    if p.status in ("timeout","transport_error"):
                        raise RuntimeError(mid+" runtime failure saved without repeat: "+str(p.error))
                write_json(work/"completed.json",{"at":time.time(),"records":len(done),"budget":budget()})
            finally:
                clean=await a.unload();write_json(work/"cleanup.json",clean)
                if not clean.get("memory_within_baseline",True):raise RuntimeError("GPU cleanup exceeded baseline")
        progress("candidate_work_complete",records=12720,run_id="abcd-test-v1",budget=budget())
        write_json(RUN/"candidate-complete.json",{"at":time.time(),"records":12720,"budget":budget(),"remaining":"independent analysis, CLI audit, disagreements, export, video updates and Astra adversarial review"})
    except BaseException as e:
        progress("needs_recovery",error=str(e),budget=budget());raise
    finally:lock.release()

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--wait-for-preflight",action="store_true")
    options=parser.parse_args();asyncio.run(main(options.wait_for_preflight))
