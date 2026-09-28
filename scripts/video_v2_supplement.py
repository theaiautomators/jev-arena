"""Report-only verification; never rewrites measured predictions."""
import json
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from arena.config import ROOT,RUNS,digest,write_json
from arena.contracts import Case
from arena.scoring import statistical_clusters,cluster_interval
RID="20260927-205440-6350b9"
p=RUNS/RID
read=lambda f:json.loads(f.read_text(encoding="utf-8"))
cases=[Case.model_validate(json.loads(x)) for x in (p/"cases.jsonl").read_text(encoding="utf-8").splitlines()]
lookup={c.id:c for c in cases}
rows=[json.loads(x) for x in (p/"predictions.jsonl").read_text(encoding="utf-8").splitlines()]
by=defaultdict(dict)
for x in rows:by[x["model_id"]][x["case_id"]]=x
excluded={x["case_id"] for x in rows if x["status"]=="unsupported"}
refs=[c for c in cases if c.label_status not in ("teacher","provisional")]
shared=[c for c in refs if c.id not in excluded]
clusters=statistical_clusters(cases)
def label(c,x):return x["selected"] in [c.gold,*c.acceptable]
pairs=[]
for cohort_name,cohort in (("all_entrant_shared_reference",shared),("all_reference",refs)):
 for mid in ("winnow","decider","nimble"):
  for metric in ("strict","selected_label"):
   def value(c,m):
    x=by[m][c.id]
    return int(label(c,x) and (metric=="selected_label" or x["status"]=="ok"))
   diffs=[value(c,mid)-value(c,"jev") for c in cohort]
   pairs.append({"cohort":cohort_name,"model":mid,"reference":"jev","metric":metric,"n":len(cohort),"delta":float(np.mean(diffs)),"ci":cluster_interval(diffs,[clusters[c.id] for c in cohort])})
follow=read(p/"followups"/"manifest.json");ids=set(follow["case_ids"])
assert len(ids)==200
summaries={}
for mid in follow["models"]:
 f=p/"followups"/"workers"/mid
 rs=[json.loads(x) for x in (f/"predictions.jsonl").read_text(encoding="utf-8").splitlines()]
 assert len(rs)==400 and {(x["case_id"],x["mode"]) for x in rs}=={(cid,mode) for cid in ids for mode in ("repeat","reversed_options")}
 for x in rs:
  c=lookup[x["case_id"]];inp=x["input"]
  assert inp["state"]==c.state and set(inp)=={"case_id","state","question"}
  assert digest(inp)==x["prediction"]["input_hash"]
  if x["mode"]=="repeat":assert inp==c.candidate()
  else:
   q=inp["question"];orig=c.question.model_dump()
   assert q["labels"]==list(reversed(orig["labels"]))
   assert all(q[k]==orig[k] for k in ("id","text","kind"))
   if isinstance(orig["criteria"],dict):assert q["criteria"]==orig["criteria"]
   elif isinstance(orig["criteria"],list):assert q["criteria"]==list(reversed(orig["criteria"]))
   else:assert q["criteria"]==orig["criteria"]
 assert read(f/"cleanup.json").get("memory_within_baseline",True)
 summary={}
 for mode in ("repeat","reversed_options"):
  cohort=[x for x in rs if x["mode"]==mode]
  comparable=[x for x in cohort if x["prediction"]["selected"] in lookup[x["case_id"]].question.labels and by[mid][x["case_id"]]["selected"] in lookup[x["case_id"]].question.labels]
  summary[mode]={"n":len(cohort),"comparable_selected_labels":len(comparable),"same_selected_as_main":sum(x["prediction"]["selected"]==by[mid][x["case_id"]]["selected"] for x in comparable),"changed_case_ids":[x["case_id"] for x in comparable if x["prediction"]["selected"]!=by[mid][x["case_id"]]["selected"]],"statuses":dict(Counter(x["prediction"]["status"] for x in cohort))}
 summaries[mid]=summary
winnow_errors=[x for x in rows if x["model_id"]=="winnow" and x["status"]=="transport_error"]
assert len(winnow_errors)==500 and all(lookup[x["case_id"]].family=="BANKING77" and len(lookup[x["case_id"]].question.labels)==77 for x in winnow_errors)
# Descriptive retrospective capability sensitivity, never a replacement result.
capacity_refs=[c for c in refs if len(c.question.labels)<=64]
capacity={m:{"n":len(capacity_refs),"strict_correct":sum(by[m][c.id]["status"]=="ok" and label(c,by[m][c.id]) for c in capacity_refs),"selected_label_correct":sum(label(c,by[m][c.id]) for c in capacity_refs)} for m in ("jev","winnow")}
run=read(p/"run.json");prog=read(ROOT/".arena/video-v2/progress.json")
assert prog["stage"]=="candidate_work_complete"
main_cost=read(p/"workers/jev/cost-ledger.json")
follow_cost=read(p/"followups/workers/jev/cost-ledger.json")
output={"run_id":RID,"followup_verification":{"records":1600,"unique_pairs_per_model":400,"input_hashes_and_reversal_meanings_verified":True,"cleanup_passed":True},"followup_comparability":summaries,"paired_intervals":pairs,"interval_note":"Descriptive unadjusted cluster-bootstrap intervals on the stated fixed cohort; not equivalence tests or population guarantees. Repeated variants share clusters.","winnow_retrospective_capacity_sensitivity":{"basis":"Post-hoc exclude all 77-label cases based on pinned native 64-label limit. Frozen errors remain unchanged.","models":capacity},"runtime":{"main_elapsed_minutes":(run["updated"]-run["created"])/60,"through_followups_minutes":(prog["updated"]-run["created"])/60,"main_started_utc_timestamp":run["created"],"main_finished_utc_timestamp":run["updated"],"followups_finished_utc_timestamp":prog["updated"],"note":"Includes interruption/resume and overlapping judge work; excludes preflight/Support Lab wait and subsequent analysis/review."},"jev_cost":{"main":main_cost,"followups":follow_cost,"combined_actual_usd":main_cost["actual_usd"]+follow_cost["actual_usd"],"combined_reserved_usd":main_cost["reserved_usd"]+follow_cost["reserved_usd"],"note":"Application ledger from reported input usage, including warmup/timing/workflows; not reconciled to provider invoice. One follow-up persistence error leaves billing uncertainty covered by reservation."}}
write_json(ROOT/"docs/evidence/full-v2-supplement.json",output)
print(json.dumps(output,indent=2))
