"""Prepare draft inputs and leak/alignment evidence; no predictions or tuning."""
import json
import time
from collections import Counter
from pathlib import Path
from tokenizers import Tokenizer
from arena.abcd import *
from arena.config import ROOT,write_json

folder=ROOT/".arena/abcd-v1";folder.mkdir(exist_ok=True)
assert not (folder/"test-freeze.json").exists(), "Test protocol already frozen; do not regenerate"
source=ROOT/".arena/research/abcd"
data,guidelines,ontology=read_sources(source)
sections=policy_sections(guidelines,ontology,json.loads((source/"kb.json").read_text(encoding="utf-8")))
tok=Tokenizer.from_file(str(ROOT/".arena/models/qwen/weights/tokenizer.json"))
summary={"stage":"draft_prepared","at":time.time(),"revision":REVISION,"test_predictions_started":False}
for split,count in (("dev",6),("test",300)):
    natural,selected=natural_cases(data,sections,ontology,count,split)
    stress=stress_cases(action_labels(ontology),tok,split)
    cases=natural+stress
    target=folder/(split+"-cases.jsonl")
    target.write_text("\n".join(c.model_dump_json() for c in cases)+"\n",encoding="utf-8")
    summary[split]={"conversation_ids":[c["convo_id"] for c in selected],"natural_cases":len(natural),"synthetic_cases":len(stress),"total":len(cases),"case_sha256":digest(target.read_bytes()),"natural_action_labels":dict(Counter(c.gold for c in natural if c.family=="action" and c.provenance["condition"]=="full_handbook")),"natural_state_tokens_qwen":{condition:sorted(len(tok.encode(c.state).ids) for c in natural if c.provenance["condition"]==condition) for condition in ("full_handbook","retrieved_policy")}}
write_json(folder/"draft-input-manifest.json",summary)
write_json(folder/"policy-sections.json",sections)
write_json(folder/"source-manifest.json",{"revision":REVISION,"files":{str(p.relative_to(source)).replace("\\","/"):digest(p.read_bytes()) for p in source.rglob("*") if p.is_file() and p.name not in ("current-suite-context.json","profile.json","guidelines-readable.txt")}})
print(json.dumps({k:{key:value for key,value in v.items() if key not in ("natural_state_tokens_qwen","conversation_ids")} if isinstance(v,dict) else v for k,v in summary.items()},indent=2))
