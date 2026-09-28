import json
import pytest
from arena.contracts import Prediction
from arena.fresh import fresh,smoke,robustness
from arena.store import Store

def test_owned_suite_counts_disjoint_ids_and_reference_separation():
    test=fresh();dev=fresh("dev");cal=fresh("calibration")
    assert (len(test),len(dev),len(cal),len(smoke()),len(robustness()))==(1440,360,360,36,1000)
    sets=[{c.cluster for c in s} for s in (test,dev,cal)]
    assert not sets[0]&sets[1] and not sets[0]&sets[2] and not sets[1]&sets[2]
    for case in test:
        public=case.candidate()
        assert set(public)=={"case_id","state","question"}
        assert "gold" not in public and "provenance" not in public

def test_counterfactual_gold_actually_changes():
    refs={c.id:c for c in fresh()}
    for c in robustness():
        anchor=refs[c.provenance["anchor_id"]]
        if c.variant=="counterfactual":assert c.gold!=anchor.gold
        else:assert c.gold==anchor.gold

def test_store_idempotency_reconnect_cursor_and_unique_predictions(tmp_path):
    s=Store(tmp_path/"test.db");req={"idempotency_key":"abcdefgh","model_ids":["m"]}
    assert s.create_run("r",req,{})==("r",True)
    assert s.create_run("r2",req,{})==("r",False)
    with pytest.raises(ValueError):s.create_run("r3",{**req,"model_ids":["n"]},{})
    first=s.event("r","stage",{"stage":"loading"});second=s.event("r","stage",{"stage":"evaluating"})
    assert [e["id"] for e in s.events("r",first)]==[second]
    p=Prediction(case_id="c",model_id="m",status="ok",selected="yes")
    s.prediction("r",p);s.prediction("r",p)
    assert len(s.predictions("r"))==1
