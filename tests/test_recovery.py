import asyncio
import json
import pytest
from arena import controller as module
from arena.contracts import RunRequest,Prediction
from arena.fresh import smoke
from arena.store import Store

@pytest.fixture
def arena(tmp_path,monkeypatch):
    runs=tmp_path/'runs';runs.mkdir()
    monkeypatch.setattr(module,'RUNS',runs);monkeypatch.setattr(module,'DATA',tmp_path)
    monkeypatch.setattr(module,'suite',lambda preset:smoke()[:8])
    ctl=module.Controller(Store(tmp_path/'store.db'))
    async def readiness():return {'models':[{'id':'uniform','name':'Uniform baseline','ready':True}], 'hardware':{},'judge':{'ready':True}}
    ctl.readiness=readiness
    class Worker:
        loads=0;unloads=0
        def __init__(self,mid,folder,cancel):self.id=mid;self.folder=folder;self.cancel=cancel;self.meta={};self.dead=False;self.cost=0;self.reserved=0
        async def load(self):Worker.loads+=1;self.folder.mkdir(parents=True,exist_ok=True)
        async def predict(self,case,cap):
            await asyncio.sleep(.003)
            if self.cancel.is_set():raise asyncio.CancelledError()
            return Prediction(case_id=case.id,model_id=self.id,status='ok',selected=case.question.labels[0],request_ms=3)
        async def unload(self):Worker.unloads+=1;return {'container_stopped':True,'memory_within_baseline':True}
    monkeypatch.setattr(module,'Adapter',Worker)
    return ctl,Worker

async def test_cancel_resume_does_not_duplicate_completed_predictions(arena):
    ctl,worker=arena
    rid=await ctl.start(RunRequest(model_ids=['uniform'],preset='smoke',judge=False,idempotency_key='cancel-resume'))
    for _ in range(500):
        if len(ctl.store.predictions(rid))>=2:break
        await asyncio.sleep(.002)
    ctl.cancel(rid);await ctl.tasks[rid]
    assert ctl.store.run(rid)['status']=='cancelled'
    before=ctl.store.predictions(rid);assert 2<=len(before)<8
    assert worker.unloads==1
    await ctl.resume(rid);await ctl.tasks[rid]
    assert ctl.store.run(rid)['status']=='complete'
    after=ctl.store.predictions(rid)
    assert len(after)==8 and len({p['case_id'] for p in after})==8
    assert all(p in after for p in before)
    assert worker.loads==worker.unloads==2
    assert json.loads((module.RUNS/rid/'results.json').read_text(encoding='utf-8'))['status']=='complete'

async def test_resume_finishes_episodes_after_quality_already_saved(arena,monkeypatch):
    ctl,worker=arena;calls=[]
    async def episodes(*args,**kwargs):
        calls.append(1)
        if len(calls)==1:raise RuntimeError('injected episode interruption')
        return []
    monkeypatch.setattr(module,'run_episodes',episodes)
    rid=await ctl.start(RunRequest(model_ids=['uniform'],preset='demo',judge=False,idempotency_key='resume-episodes'))
    await ctl.tasks[rid]
    assert len(ctl.store.predictions(rid))==8
    assert ctl.store.run(rid)['status']=='failed'
    await ctl.resume(rid);await ctl.tasks[rid]
    assert ctl.store.run(rid)['status']=='complete'
    assert len(ctl.store.predictions(rid))==8 and len(calls)==2
    assert worker.loads==worker.unloads==2

async def test_changed_runtime_cannot_resume(arena,monkeypatch):
    ctl,_=arena
    rid=await ctl.start(RunRequest(model_ids=['uniform'],preset='smoke',judge=False,idempotency_key='fingerprint-change'))
    ctl.cancel(rid);await ctl.tasks[rid]
    async def changed(ids):return {'different':'runtime'}
    monkeypatch.setattr(module,'runtime_fingerprint',changed)
    with pytest.raises(ValueError,match='changed'):await ctl.resume(rid)

async def test_memory_cleanup_failure_stops_cascade(arena,monkeypatch):
    ctl,worker=arena
    async def failed_cleanup(self):return {'memory_within_baseline':False}
    monkeypatch.setattr(worker,'unload',failed_cleanup)
    rid=await ctl.start(RunRequest(model_ids=['uniform'],preset='smoke',judge=False,idempotency_key='memory-gate'))
    await ctl.tasks[rid]
    assert ctl.store.run(rid)['status']=='failed'
    assert 'memory' in ctl.store.run(rid)['error']
