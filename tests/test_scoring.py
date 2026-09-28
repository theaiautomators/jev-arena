import math
import pytest
from arena.contracts import Case,Question,Prediction
from arena.scoring import validate_prediction,summarize,paired,cluster_interval,statistical_clusters

def fixture(kind="noul"):
    return Case(id="x",cluster="a",pack="test",family="test",state="Flag is on.",question=Question(id="q",kind=kind,text="Is flag on?",labels=["no","yes"]),gold="yes")

def prediction(**kwargs):
    return Prediction(case_id="x",model_id="m",status="ok",selected="yes",probabilities={"no":.2,"yes":.8},**kwargs)

def test_binary_brier_and_nll_are_independently_known():
    m=summarize([fixture()],[prediction().model_dump()])
    assert m["brier_binary"]==pytest.approx(.04)
    assert m["nll"]==pytest.approx(-math.log(.8))
    assert m["ece"]==pytest.approx(.2)
    assert m["accuracy_ci"]==[1,1]

@pytest.mark.parametrize("probs",[{"no":.2,"yes":.9},{"yes":1},{"no":float('nan'),"yes":1},{"no":-.1,"yes":1.1}])
def test_invalid_distributions_never_enter_calibration(probs):
    p=prediction();p.probabilities=probs
    p=validate_prediction(p,fixture())
    assert p.status=="invalid"
    metrics=summarize([fixture()],[p.model_dump()])
    assert metrics["probability_count"]==0
    assert metrics['accuracy']==0 and metrics['selected_label_accuracy']==1
    assert metrics['output_contract_failures']==1

def test_failure_denominator_and_unsupported_coverage():
    cases=[fixture().model_copy(update={"id":str(i)}) for i in range(3)]
    rows=[prediction().model_copy(update={"case_id":"0"}).model_dump(),Prediction(case_id="1",model_id="m",status="timeout").model_dump(),Prediction(case_id="2",model_id="m",status="unsupported").model_dump()]
    m=summarize(cases,rows)
    assert m["accuracy"]==.5
    assert m["coverage"]==pytest.approx(1/3)
    assert m["unsupported"]==1

def test_multiclass_convention_is_sum_not_mean():
    c=fixture("choice");p=prediction()
    assert summarize([c],[p.model_dump()])["brier_multiclass"]==pytest.approx(.08)

def test_paired_interval_clusters_related_questions():
    assert cluster_interval([1,1,-1,-1],["a","a","b","b"],repeats=1000)==[-1,1]
    p=prediction();q=prediction();q.selected="no"
    assert paired([fixture()],[p.model_dump()],[q.model_dump()])["ci"]==[1,1]

def test_no_probability_fabrication():
    p=prediction();p.probabilities=None
    m=summarize([fixture()],[p.model_dump()])
    assert m["accuracy"]==1
    assert m["ece"] is None and m["nll"] is None

@pytest.mark.parametrize('total',[.9999,1.0001])
def test_rounding_boundary_includes_binary_float_representation(total):
    p=prediction();p.probabilities={'no':.2,'yes':total-.2}
    checked=validate_prediction(p,fixture())
    assert checked.status=='ok' and checked.normalized_rounding
    assert math.fsum(checked.probabilities.values())==pytest.approx(1)

def test_rounding_guard_does_not_expand_the_declared_tolerance():
    p=prediction();p.probabilities={'no':.2,'yes':.7998}
    assert validate_prediction(p,fixture()).status=='invalid'


def test_duplicate_inputs_connect_related_clusters_transitively():
    a=fixture().model_copy(update={'id':'a','cluster':'first'})
    b=a.model_copy(update={'id':'b','cluster':'second'})
    c=b.model_copy(update={'id':'c','state':'Another state'})
    d=c.model_copy(update={'id':'d','cluster':'third'})
    distinct=a.model_copy(update={'id':'e','cluster':'fourth','state':'Distinct state'})
    groups=statistical_clusters([a,b,c,d,distinct])
    assert len({groups[k] for k in ('a','b','c','d')})==1
    assert groups['e']!=groups['a']

def test_teacher_is_excluded_from_verified_accuracy_and_calibration():
    verified=fixture();teacher=fixture().model_copy(update={'id':'t','label_status':'teacher','gold':'no','reference_probs':{'no':.9,'yes':.1}})
    p=prediction();t=p.model_copy(update={'case_id':'t'})
    m=summarize([verified,teacher],[p.model_dump(),t.model_dump()])
    assert m['accuracy']==1 and m['teacher_agreement']==0
    assert m['probability_count']==1 and m['teacher_count']==1
    assert m['teacher_brier']==pytest.approx(.98)
    assert m['ece']==pytest.approx(.2)
