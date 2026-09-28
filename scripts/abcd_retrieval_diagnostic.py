"""Corrected post-execution retrieval coverage using upstream step annotations."""
import json
import gzip
from collections import Counter
from arena.config import ROOT, write_json, digest
from arena.contracts import Case
from scripts.analyze_abcd import FOLDER, RUN, summarize

def main():
    cases = [Case.model_validate_json(x) for x in (FOLDER/"test-cases.jsonl").read_text(encoding="utf-8").splitlines()]
    raw = ROOT/".arena/research/abcd/abcd_v1.1.json.gz"
    data = json.loads(gzip.decompress(raw.read_bytes()))
    conversations = {c["convo_id"]:c for c in data["test"]}
    sections = {s["id"] for s in json.loads((FOLDER/"policy-sections.json").read_text(encoding="utf-8"))}
    target_procedure = {}; transitions = Counter()
    natural = [c for c in cases if c.pack == "ABCD next action" and c.provenance["condition"] == "retrieved_policy"]
    for c in natural:
        p = c.provenance; conv = conversations[p["conversation_id"]]; i = p["checkpoint_index"]
        # End checkpoints inherit the last observed turn's annotated procedure.
        step = conv["delexed"][min(i,len(conv["delexed"])-1)]
        target = step["targets"][0]
        assert target in sections
        target_procedure[c.id] = target
        old = p["source_intent_for_analysis_only"] in p["retrieved_sections"]
        new = target in p["retrieved_sections"]
        transitions[(c.family,old,new)] += 1
    models = {}
    for mid in ("jev","decider","winnow","nimble","qwen"):
        rows = [json.loads(x) for x in (RUN/"workers"/mid/"predictions.jsonl").read_text(encoding="utf-8").splitlines()]
        lookup = {r["prediction"]["case_id"]:r for r in rows}
        models[mid] = {}
        for task in ("route","action"):
            group = [c for c in natural if c.family == task]
            hit = [c for c in group if target_procedure[c.id] in c.provenance["retrieved_sections"]]
            miss = [c for c in group if c not in hit]
            models[mid][task] = {"hit":summarize(hit,lookup),"miss":summarize(miss,lookup)}
    out = {"id":"abcd-test-v1","status":"reporting correction; inference and scores unchanged",
           "source_sha256":digest(raw.read_bytes()),
           "method":"Actual annotated step subflow from upstream targets[0]; synthesized end inherits the last observed turn. Analysis only: annotations are never supplied to retrieval or candidates.",
           "old_method":"Exact scenario.subflow string compared with the 55 section IDs; fine-grained FAQ names and occasional scenario/dialogue disagreement caused misleading coverage.",
           "transitions":[{"task":t,"old_hit":a,"corrected_hit":b,"n":n} for (t,a,b),n in sorted(transitions.items())],
           "models":models,
           "limits":"Annotated-procedure coverage is not human-verified semantic sufficiency; one checkpoint can reasonably involve more than one procedure. No score or gold edits."}
    write_json(ROOT/"docs/evidence/abcd-retrieval-correction.json",out)
    print(json.dumps({"route_hit":models["jev"]["route"]["hit"]["planned"],"action_hit":models["jev"]["action"]["hit"]["planned"],"transitions":out["transitions"]}))

if __name__ == "__main__": main()
