import json
import pytest
from arena import judge
from arena.config import digest
from arena.contracts import Case,Question
from scripts.audit_abcd import select_jobs,batches,recover_result


def test_audit_deduplicates_and_blinds_model_reference_and_metadata():
    c=Case(id="source-case",cluster="conversation",pack="ABCD next action",family="action",state="Observed evidence",question=Question(id="decision",text="Next?",kind="choice",labels=["a","b"]),gold="a",provenance={"condition":"full_handbook","secret_scenario":"never expose"})
    ps=[{"case_id":c.id,"model_id":m,"status":s,"selected":a} for m,s,a in [("one","ok","a"),("two","invalid","a"),("three","ok","b"),("four","unsupported",None)]]
    jobs=select_jobs([c],ps,{c.id})
    assert len(jobs)==2
    correct=next(j for j in jobs if j["item"]["proposed_answer"]=="a")
    assert correct["models"]==["one","two"]
    assert set(correct["item"])=={"case_id","question_id","state","question","rubric","allowed_answers","proposed_answer"}
    assert correct["item"]["case_id"]!=c.id
    assert "never expose" not in json.dumps(correct["item"])
    assert select_jobs([c],list(reversed(ps)),{c.id})==jobs


def test_batches_bound_size_count_and_keep_same_question_apart():
    jobs=[{"id":str(i),"original_case_id":str(i//2),"item":{"case_id":str(i),"state":"x"*20}} for i in range(20)]
    grouped=batches(jobs,max_chars=300)
    assert sorted(int(j["id"]) for b in grouped for j in b)==list(range(20))
    for b in grouped:
        assert len(b)<=8 and len({j["original_case_id"] for j in b})==len(b)
        assert len(json.dumps([j["item"] for j in b],ensure_ascii=False))<=300
    with pytest.raises(ValueError):batches(jobs,max_chars=10)


def test_recover_windows_newlines_without_another_judge_call(tmp_path):
    items=[{"case_id":"opaque","question_id":"decision","state":"line1\nline2","proposed_answer":"a"}]
    prompt="Rubric\nDATA:\n"+json.dumps(items)
    (tmp_path/"prompt.txt").write_bytes(prompt.replace("\n","\r\n").encode())
    grade={"case_id":"opaque","question_id":"decision","verdict":"correct","evidence":"line1","rationale":"Supported","needs_human_review":False}
    (tmp_path/"answer.json").write_text(json.dumps({"grades":[grade]}),encoding="utf-8")
    meta={"exit_code":0,"tool_events":[],"requested_model":judge.MODEL,"rubric_version":judge.VERSION,"prompt_sha256":digest(prompt.encode()),"schema_sha256":digest(judge.SCHEMA)}
    (tmp_path/"metadata.json").write_text(json.dumps(meta),encoding="utf-8")
    assert recover_result(tmp_path,items)["grades"]==[grade]
    with pytest.raises(AssertionError):recover_result(tmp_path,[{**items[0],"proposed_answer":"b"}])
