"""Blinded, deduplicated ABCD reference audit through Codex CLI only."""
from __future__ import annotations
import argparse
import asyncio
import json
import time
from collections import defaultdict, Counter
from pathlib import Path
import jsonschema
from filelock import FileLock
from arena import judge
from arena.config import DATA, ROOT, digest, write_json
from arena.contracts import Case
from scripts.analyze_abcd import FOLDER, RUN

AUDIT = RUN / "audit"
MAX_CHARS = 240000  # conservative payload bound; actual CLI usage is recorded, not inferred from characters


def select_jobs(cases, predictions, audit_ids):
    lookup = {c.id:c for c in cases}
    groups = defaultdict(set)
    for p in predictions:
        if p["case_id"] not in audit_ids: continue
        c = lookup[p["case_id"]]
        if p["status"] in ("ok","invalid") and p.get("selected") in c.question.labels:
            groups[c.id,p["selected"]].add(p["model_id"])
    jobs = []
    for (cid, answer), models in groups.items():
        c = lookup[cid]
        jid = digest([cid, answer, judge.VERSION])[:24]
        # Opaque review ID prevents model/source/gold attribution in the judge payload.
        item = {"case_id":jid,"question_id":c.question.id,"state":c.state,
                "question":c.question.text,"rubric":c.question.rubric,
                "allowed_answers":c.question.labels,"proposed_answer":answer}
        jobs.append({"id":jid,"original_case_id":cid,"models":sorted(models),"item":item,
                     "reference":c.gold,"condition":c.provenance["condition"],"task":c.family})
    return sorted(jobs,key=lambda j:j["id"])


def batches(jobs, max_chars=MAX_CHARS):
    pending = list(jobs); output = []
    while pending:
        batch = []; seen = set(); size = 2
        for job in pending:
            length = len(json.dumps(job["item"],ensure_ascii=False))+2
            if length+2 > max_chars: raise ValueError("One audit item exceeds the declared payload budget")
            if job["original_case_id"] in seen or size+length > max_chars: continue
            batch.append(job); seen.add(job["original_case_id"]); size += length
            if len(batch) == 8: break
        assert batch
        selected = {j["id"] for j in batch}
        output.append(batch); pending = [j for j in pending if j["id"] not in selected]
    return output


def recover_result(folder, items):
    """Recover a finished CLI response after an interrupted local import, without a repeat call."""
    names = ("answer.json","metadata.json","prompt.txt")
    if not all((folder/name).exists() for name in names): return None
    meta = json.loads((folder/"metadata.json").read_text(encoding="utf-8"))
    if meta["exit_code"] != 0 or meta["tool_events"]: return None
    assert meta["requested_model"] == judge.MODEL and meta["rubric_version"] == judge.VERSION
    prompt = (folder/"prompt.txt").read_text(encoding="utf-8")
    assert digest(prompt.encode()) == meta["prompt_sha256"]
    assert digest(judge.SCHEMA) == meta["schema_sha256"]
    assert json.loads(prompt.split("\nDATA:\n",1)[1]) == items
    result = json.loads((folder/"answer.json").read_text(encoding="utf-8"))
    jsonschema.validate(result,judge.SCHEMA)
    expected = {(i["case_id"],i["question_id"]) for i in items}
    got = [(g["case_id"],g["question_id"]) for g in result["grades"]]
    assert len(got) == len(expected) and set(got) == expected
    return {"grades":result["grades"],"metadata":meta}


def progress(stage, **kw):
    value = {"stage":stage,"updated":time.time(),**kw}
    write_json(AUDIT/"progress.json",value)
    print(json.dumps(value),flush=True)


def usage():
    total = Counter(); calls = []; observed = set()
    for eventfile in sorted((AUDIT/"batches").glob("*/attempt-*/events.jsonl")):
        tokens = Counter()
        for line in eventfile.read_text(encoding="utf-8").splitlines():
            try: event = json.loads(line)
            except ValueError: continue
            if event.get("type") == "turn.completed":
                tokens.update({k:v for k,v in event.get("usage",{}).items() if isinstance(v,(int,float))})
        total.update(tokens)
        meta = eventfile.parent/"metadata.json"
        metadata = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}
        if metadata.get("observed_model"): observed.add(metadata["observed_model"])
        calls.append({"path":str(eventfile.parent.relative_to(AUDIT)),"usage":dict(tokens),
                      "exit_code":metadata.get("exit_code"),"elapsed_ms":metadata.get("elapsed_ms")})
    return {"calls":len(calls),"tokens":dict(total),"attempts":calls,"requested_model":judge.MODEL,
            "observed_models":sorted(observed),"billing":"Saved CLI token usage; not observed cash spend or billed credits. Reasoning/cache detail may be included in parent totals."}


async def main(wait=False):
    AUDIT.mkdir(parents=True,exist_ok=True)
    with FileLock(AUDIT/"worker.lock",timeout=0):
        while not (RUN/"candidate-complete.json").exists():
            if not wait: raise RuntimeError("Candidates incomplete")
            progress("waiting_for_candidates")
            await asyncio.sleep(30)
        # Candidate evidence must independently verify before sending any audit requests.
        from scripts.analyze_abcd import main as analyze
        progress("verifying_candidates")
        try:
            await asyncio.to_thread(analyze)
        except BaseException as error:
            progress("needs_attention",phase="independent_verification",error=str(error))
            raise
        frozen = json.loads((FOLDER/"test-freeze.json").read_text(encoding="utf-8"))
        assert frozen["judge"]["requested_model"] == judge.MODEL
        assert frozen["judge"]["rubric"] == judge.VERSION
        assert json.loads((DATA/"judge-controls"/judge.VERSION/"report.json").read_text(encoding="utf-8"))["passed"]
        cases = [Case.model_validate_json(x) for x in (FOLDER/"test-cases.jsonl").read_text(encoding="utf-8").splitlines()]
        predictions = []
        for mid in frozen["order"]:
            predictions.extend(json.loads(line)["prediction"] for line in (RUN/"workers"/mid/"predictions.jsonl").read_text(encoding="utf-8").splitlines())
        jobs = select_jobs(cases,predictions,set(frozen["audit_case_ids"]))
        planned = {"frozen_cases":frozen["audit_case_ids"],"jobs":jobs,"rubric":judge.VERSION,
                   "max_batch_answers":8,"max_payload_characters":MAX_CHARS,
                   "script_sha256":digest(Path(__file__).read_bytes()),
                   "judge_sha256":digest((ROOT/"arena/judge.py").read_bytes())}
        if (AUDIT/"plan.json").exists(): assert json.loads((AUDIT/"plan.json").read_text(encoding="utf-8")) == planned, "Audit plan changed"
        else:
            write_json(AUDIT/"plan.json",planned)
            (AUDIT/"script-snapshot.py").write_bytes(Path(__file__).read_bytes())
        try:
            total_batches = batches(jobs)
            for number, batch in enumerate(total_batches):
                items = [j["item"] for j in batch]
                paths = [AUDIT/"grades"/(j["id"]+".json") for j in batch]
                if all(p.exists() for p in paths):
                    for job,path in zip(batch,paths):
                        saved=json.loads(path.read_text(encoding="utf-8"));assert saved["item_sha256"] == digest(job["item"])
                    continue
                folder = AUDIT/"batches"/digest(items)[:24]
                existing = sorted(folder.glob("attempt-*"),key=lambda p:int(p.name.split("-")[-1]))
                result = None
                for attempt in existing:
                    recovered = recover_result(attempt,items)
                    if recovered is not None:
                        result=recovered;break
                if result is None:
                    start = max([int(p.name.split("-")[-1]) for p in existing]+[0])+1
                    for offset in range(2):
                        attempt = folder/("attempt-"+str(start+offset))
                        progress("judging",batch=number+1,batches=len(total_batches),answers=len(jobs))
                        try:
                            result = await judge.grade(items,attempt)
                            break
                        except judge.JudgePaused: raise
                        except Exception:
                            if offset == 1: raise
                assert result is not None
                grades = {g["case_id"]:g for g in result["grades"]}
                for job,path in zip(batch,paths):
                    value = {"job_id":job["id"],"original_case_id":job["original_case_id"],"models":job["models"],
                             "item_sha256":digest(job["item"]),"grade":grades[job["id"]],"metadata":result["metadata"]}
                    if path.exists(): assert json.loads(path.read_text(encoding="utf-8")) == value
                    else: write_json(path,value)
                write_json(AUDIT/"usage.json",usage())
            grades = [json.loads((AUDIT/"grades"/(j["id"]+".json")).read_text(encoding="utf-8")) for j in jobs]
            flags = []
            for job,g in zip(jobs,grades):
                verdict = g["grade"]["verdict"]
                reference_match = job["item"]["proposed_answer"] == job["reference"]
                disagreement = (reference_match and verdict == "incorrect") or (not reference_match and verdict in ("correct","acceptable"))
                if disagreement or verdict == "ambiguous" or g["grade"]["needs_human_review"]:
                    flags.append({**g,"reference":job["reference"],"proposed_answer":job["item"]["proposed_answer"],
                                  "condition":job["condition"],"task":job["task"],"reference_disagreement":disagreement})
            report = {"stage":"audit_complete_pending_inspection","at":time.time(),"selected_questions":len(frozen["audit_case_ids"]),
                      "judged_questions":len({j["original_case_id"] for j in jobs}),"answer_reviews":len(jobs),
                      "selected_without_usable_answers":sorted(set(frozen["audit_case_ids"])-{j["original_case_id"] for j in jobs}),
                      "verdicts":dict(Counter(g["grade"]["verdict"] for g in grades)),"flags":flags,
                      "usage":usage(),"human_audit":False,"gold_changed":False}
            write_json(AUDIT/"report.json",report)
            progress("audit_complete_pending_inspection",questions=report["judged_questions"],answer_reviews=len(jobs),flags=len(flags))
        except BaseException as error:
            write_json(AUDIT/"usage.json",usage())
            progress("needs_attention",error=type(error).__name__+": "+str(error))
            raise


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--wait-candidates",action="store_true")
    asyncio.run(main(parser.parse_args().wait_candidates))
