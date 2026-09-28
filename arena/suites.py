from __future__ import annotations
import json
from collections import Counter
from arena.config import DATASETS, SOURCES, digest, write_json
from arena.contracts import Case, Question
from arena.fresh import fresh, smoke, robustness

EXPECTED = {"JevBench public":231,"Typed decisions":2000,"Classification":1500,"Multilingual":1000,"RAG relevance":500,"Arena Fresh":1440,"Robustness":1000}

def jevbench():
    out=[]
    for tier in ("original","easy","hard"):
        path=SOURCES/"jevbench"/"datasets"/"public"/f"{tier}.jsonl"
        if not path.exists(): continue
        for line in path.read_text(encoding="utf-8").splitlines():
            x=json.loads(line);q=x["question"]
            x["group"]=x.get("group") or x["id"]
            criteria=q.get("criteria",{})
            out.append(Case(id="jevbench-"+x["id"],cluster="jevbench-"+x.get("group",x["id"]),pack="JevBench public",family=x["family"],state=x["state"] if isinstance(x["state"],str) else json.dumps(x["state"]),question=Question(id="decision",text=q["instructions"],kind=q["type"],labels=x["labels"],rubric=json.dumps(criteria,ensure_ascii=False)),gold=str(x["expected"]),label_status="public",provenance={**x.get("provenance",{}),"tier":tier,"file_sha256":digest(path.read_bytes()),"native_question":q}))
    for case in out:
        case.question.criteria=case.provenance["native_question"].get("criteria")
    return out

def imported():
    result=[]
    for path in sorted(DATASETS.glob("*-cases.jsonl")):
        result.extend(Case.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return result

def suite(preset):
    if preset=="smoke": cases=smoke()
    elif preset=="demo":
        pool=jevbench()
        if len(pool)<84:raise ValueError('Demo needs the pinned public JevBench sources. Use Prepare selected in Setup first.')
        cases=smoke()+pool[:84]
    else:
        cases=jevbench()+imported()+fresh()+robustness()
        counts=Counter(c.pack for c in cases)
        missing={k:{"expected":v,"available":counts.get(k,0)} for k,v in EXPECTED.items() if counts.get(k,0)!=v}
        if missing: raise ValueError("Full suite is not prepared: "+json.dumps(missing))
    if len({c.id for c in cases})!=len(cases): raise ValueError("Duplicate case IDs in suite")
    return cases

def inventory():
    counts=Counter(c.pack for c in jevbench()+imported()+fresh()+robustness())
    return {"version":"arena-v2","expected":7671,"available":sum(counts.values()),"packs":[{"name":k,"expected":v,"available":counts[k],"ready":counts[k]==v} for k,v in EXPECTED.items()],"presets":[{"id":"smoke","count":36,"ready":True},{"id":"demo","count":120,"ready":counts['JevBench public']>=84},{"id":"full","count":7671,"ready":all(counts[k]==v for k,v in EXPECTED.items())}],"fresh_status":"Executable-policy fixtures v2: new seed, explicit routing and approval rules. Human semantic audit not claimed."}
