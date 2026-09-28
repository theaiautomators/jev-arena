import json
from types import SimpleNamespace
import pytest
from scripts import abcd_preflight as pre
from scripts import run_abcd_assessment as run

def test_combined_budget_preserves_both_v2_and_all_abcd_ledgers(tmp_path,monkeypatch):
    base=tmp_path/'v2';abcd=tmp_path/'abcd'
    paths=[base/'workers/jev/cost-ledger.json',base/'followups/workers/jev/cost-ledger.json',abcd/'runs/dev/workers/jev/cost-ledger.json',abcd/'runs/test/workers/jev/cost-ledger.json']
    for p,v in zip(paths,[.24,.014,.01,.9]):
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'actual_usd':v-.001,'reserved_usd':v}),encoding='utf-8')
    archive=abcd/'recovery/cost-ledger.snapshot.json';archive.parent.mkdir(parents=True);archive.write_text(json.dumps({'actual_usd':999,'reserved_usd':999}),encoding='utf-8')
    monkeypatch.setattr(pre,'BASE_LEDGER',base);monkeypatch.setattr(pre,'FOLDER',abcd)
    result=pre.budget()
    assert result['combined_cap_usd']==6 and result['ledgers']==4
    assert result['reserved_usd']==pytest.approx(1.164)

@pytest.mark.asyncio
async def test_exhausted_combined_budget_prevents_adapter_call(monkeypatch):
    monkeypatch.setattr(pre,'budget',lambda:{'reserved_usd':6.01})
    class Adapter:
        reserved=0
        async def predict(self,*args,**kwargs):pytest.fail('No paid request may be made')
    with pytest.raises(RuntimeError,match='cap exhausted'):await pre.predict(Adapter(),None)

def test_resume_drift_rejected_before_accepting_existing_freeze(tmp_path,monkeypatch):
    path=tmp_path/'test-freeze.json';path.write_text(json.dumps({'fingerprint':{'old':1}}),encoding='utf-8')
    monkeypatch.setattr(run,'FOLDER',tmp_path);monkeypatch.setattr(run,'fingerprint',lambda:{'new':1})
    with pytest.raises(AssertionError,match='drift'):run.freeze([])
    assert json.loads(path.read_text())['fingerprint']=={'old':1}

def test_audit_selection_independent_of_gold_answer():
    cases=[]
    for task in ['route','action']:
        for condition in ['full_handbook','retrieved_policy']:
            for i in range(20):cases.append(SimpleNamespace(id=f'{task}-{condition}-{i}',family=task,pack='ABCD next action',provenance={'condition':condition},gold='one'))
    for length in [4096,8192,16384,28672]:
        for position in ['early','middle','late']:
            for i in range(2):cases.append(SimpleNamespace(id=f'{length}-{position}-{i}',family='synthetic_action',pack='Controlled context stress',provenance={'target_state_tokens_qwen':length,'evidence_position':position},gold='one'))
    before=run.audit_ids(cases)
    for c in cases:c.gold='different'
    assert before==run.audit_ids(list(reversed(cases))) and len(before)==76
