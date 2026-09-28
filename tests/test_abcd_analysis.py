import pytest
from arena.contracts import Case, Question
from scripts.analyze_abcd import observation, rates, classification, combined, paired, interval


def case(cid, gold, task="route", idx=1, labels=None):
    labels = labels or ["take_action", "retrieve_utterance", "end_conversation"]
    return Case(id=cid, cluster="conversation-1", pack="ABCD next action", family=task,
                state="Visible history", question=Question(id="decision", text="Next?", kind="choice", labels=labels),
                gold=gold, provenance={"checkpoint_index":idx,"condition":"full_handbook"})


def row(c, selected, status="ok"):
    return {"prediction":{"case_id":c.id,"selected":selected,"status":status}}


def test_wrong_capacity_is_not_counted_as_incorrect_supported_answer():
    a=case("a","take_action"); b=case("b","retrieve_utterance"); c=case("c","end_conversation")
    obs=[observation(a,row(a,"take_action","invalid")),observation(b,row(b,"retrieve_utterance")),observation(c,row(c,None,"unsupported"))]
    r=rates(obs)
    assert r["planned"]==3 and r["supported"]==2 and r["unsupported"]==1
    assert r["label_accuracy_supported"]==1 and r["strict_accuracy_supported"]==.5
    assert r["label_correct_yield_planned"]==pytest.approx(2/3)
    assert r["strict_correct_yield_planned"]==pytest.approx(1/3)


def test_macro_f1_uses_all_declared_labels_and_invalid_outputs_are_separate():
    a=case("a","a",task="action",labels=["a","b","c"])
    b=case("b","b",task="action",labels=["a","b","c"])
    rows={a.id:row(a,"a","invalid"),b.id:row(b,"a")}
    r=classification([a,b],rows)
    assert r["strict"]["macro_f1"]==0
    assert r["label"]["macro_f1"]==pytest.approx((2/3)/3)
    assert r["label"]["per_label"][2]["support"]==0


def test_combined_requires_both_route_and_action_and_retains_capacity_gap():
    route=case("route","take_action"); action=case("action","tool-a",task="action",labels=["tool-a","tool-b"])
    rows={route.id:row(route,"retrieve_utterance"),action.id:row(action,"tool-a")}
    result=combined([route,action],rows,"full_handbook")[0]
    assert result["supported"] and not result["strict"] and not result["label"]
    rows[route.id]=row(route,"take_action"); rows[action.id]=row(action,None,"unsupported")
    result=combined([route,action],rows,"full_handbook")[0]
    assert not result["supported"] and result["status"]=="unsupported"


def test_paired_excludes_unshared_capacity_and_bootstrap_keeps_cluster():
    a=[{"cluster":"c1","supported":True,"strict":True,"label":True}, {"cluster":"c2","supported":False,"strict":False,"label":False}]
    b=[{"cluster":"c1","supported":True,"strict":False,"label":True}, {"cluster":"c2","supported":True,"strict":True,"label":True}]
    result=paired(a,b)
    assert result["shared_supported"]==1
    assert result["strict"]["difference"]==-1 and result["label"]["difference"]==0
    assert interval([1,0],["same","same"])==[.5,.5]
    assert rates([])["strict_accuracy_supported"] is None


def test_provider_failure_usage_stays_unknown_but_success_cannot_omit_tokens():
    from scripts.analyze_abcd import verify_token_accounting
    assert verify_token_accounting({"status":"transport_error","input_tokens":None,"selected":None}) is False
    assert verify_token_accounting({"status":"ok","input_tokens":234,"selected":"a"}) is True
    with pytest.raises(AssertionError):verify_token_accounting({"status":"ok","input_tokens":None,"selected":"a"})
    with pytest.raises(AssertionError):verify_token_accounting({"status":"unsupported","input_tokens":None,"selected":None})
