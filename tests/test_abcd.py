import ast
import copy
import json
from pathlib import Path
import pytest
from arena.abcd import *

SOURCE=Path(".arena/research/abcd")
@pytest.fixture(scope="module")
def source():
    if not (SOURCE/"abcd_v1.1.json.gz").exists():pytest.skip("pinned ABCD download is not present")
    return read_sources(SOURCE)

def test_history_is_prefix_only():
    c={"delexed":[{"speaker":"customer","text":"observed","targets":["secret"]},{"speaker":"action","text":"TARGET OUTCOME","targets":["hidden"]}]}
    assert observed_history(c,1)=="customer: observed"
    with pytest.raises(ValueError):observed_history(c,3)

def test_full_candidate_excludes_current_future_and_scenario(source):
    data,g,o=source;sections=policy_sections(g,o);retriever=PolicyRetriever(sections)
    c=data["dev"][0];point=next(p for p in checkpoints(c) if p["route"]=="take_action")
    original=make_case(c,point,"retrieved_policy","action",sections,action_labels(o),retriever)
    altered=copy.deepcopy(c);altered["scenario"]={"subflow":"HIDDEN_SCENARIO"}
    for turn in altered["delexed"][point["index"]:]:turn["text"]="TARGET_OR_FUTURE_SENTINEL"
    for turn in altered["delexed"]:turn["targets"]=["SECRET_TARGET"]*5;turn["candidates"]=["SECRET_CANDIDATE"]
    after=make_case(altered,point,"retrieved_policy","action",sections,action_labels(o),retriever)
    assert original.candidate()==after.candidate()
    assert set(original.candidate())=={"case_id","state","question"}
    assert len(original.question.labels)==30

def test_alignment_matches_pinned_upstream_cds_feature_boundary(source):
    data,_,_=source
    path=SOURCE/"upstream/utils/process.py"
    if not path.exists():pytest.skip("pinned preparation source not present")
    tree=ast.parse(path.read_text(encoding="utf-8"))
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="CDSProcessor")
    method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="build_features")
    # Execute only the inspected upstream boundary loop; model/slot/token code
    # is replaced by collectors because this adaptation scores action labels.
    ns={"progress_bar":lambda rows,**_:rows}
    exec(compile(ast.Module(body=[method],type_ignores=[]),str(path),"exec"),ns)
    class Capture:
        def __init__(self):self.got=[]
        def collect_one_example(self,context,targets,support):self.got.append((context.copy(),targets[1],targets[2] if targets[1]=="take_action" else None))
        def collect_examples(self,context,targets,*_):self.collect_one_example(context,targets,None)
    for c in select_conversations(data,300,"test"):
        cap=Capture();ns["build_features"](cap,None,{"test":[c]})
        ours=[(observed_history(c,p["index"]),p["route"],p["action"]) for p in checkpoints(c)]
        reference=[("\n".join(v.replace("|",": ",1) for v in history),route,action) for history,route,action in cap.got]
        assert ours==reference

def test_selection_is_frozen_by_ids_not_input_order(source):
    data,g,o=source
    first=select_conversations(data,300);shuffled={k:list(reversed(v)) for k,v in data.items()}
    assert [c["convo_id"] for c in first]==[c["convo_id"] for c in select_conversations(shuffled,300)]
    sections=policy_sections(g,o);cases,_=natural_cases(data,sections,o,300)
    assert len(cases)==2400 and len({c.id for c in cases})==2400
    assert len({c.cluster for c in cases})==300
    assert Counter(c.family for c in cases)=={"route":1800,"action":600}
    assert all(len(c.question.labels)==30 for c in cases if c.family=="action")
    assert len({c.gold for c in cases if c.family=="route"})==3

def test_retrieval_has_no_target_dependency():
    sections=[{"id":"b","text":"password reset identity"},{"id":"a","text":"warehouse shipping return"}]
    retriever=PolicyRetriever(sections,k=1)
    assert retriever.retrieve("customer: forgot password")[0]["id"]=="b"
    assert retriever.retrieve("customer: shipping return")[0]["id"]=="a"


def test_public_catalog_and_aliases_available_equally(source):
    data,g,o=source;kb=json.loads((SOURCE/"kb.json").read_text(encoding="utf-8"))
    sections=policy_sections(g,o,kb)
    for section in sections:
        assert ", ".join(kb[section["id"]]) in section["text"]
    point=next(p for p in checkpoints(data["dev"][0]) if p["route"]=="take_action")
    for condition in ("full_handbook","retrieved_policy"):
        c=make_case(data["dev"][0],point,condition,"action",sections,action_labels(o),PolicyRetriever(sections))
        assert "Notify Internal Team = notify-team" in c.state
