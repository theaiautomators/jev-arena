"""Separate performance blocks; serialized-worker limits are explicitly reported."""
import asyncio
import time
import numpy as np
from arena.config import write_json
from arena.hardware import hardware

async def measure(adapter,cases,folder,cap):
    pack=[cases[i%len(cases)] for i in range(200)];blocks=[]
    # One stdin stream cannot multiplex calls. Native concurrent serving requires a
    # separate adapter profile; never fake its scaling by dividing serial latency.
    for block in range(3):
        start=time.perf_counter();preds=[];samples=[];stop=asyncio.Event()
        async def sample():
            while not stop.is_set():
                gpu=(await asyncio.to_thread(hardware)).get('gpu')
                if gpu:samples.append({'elapsed_s':time.perf_counter()-start,**gpu})
                try:await asyncio.wait_for(stop.wait(),1)
                except asyncio.TimeoutError:pass
        telemetry=asyncio.create_task(sample())
        try:
            for case in pack:preds.append((await adapter.predict(case,cap)).model_dump())
        finally:
            stop.set();await telemetry
        elapsed=time.perf_counter()-start
        result={'block':block,'concurrency':1,'cache_mode':'no full-response cache','requests':200,'valid':sum(p['status']=='ok' for p in preds),'elapsed_s':elapsed,'requests_per_second':200/elapsed,'p50_ms':float(np.median([p['request_ms'] for p in preds])),'p95_ms':float(np.quantile([p['request_ms'] for p in preds],.95)),'predictions':preds}
        result['telemetry']=samples
        powers=[s for s in samples if s.get('power_w') is not None]
        result['gpu_energy_wh']=sum((b['elapsed_s']-a['elapsed_s'])*(a['power_w']+b['power_w'])/2/3600 for a,b in zip(powers,powers[1:])) if len(powers)>1 else None
        result['energy_scope']='Whole-GPU sampled estimate during block; includes other GPU users, excludes CPU/display and unobserved edge intervals.'
        result['valid_decisions_per_second']=result['valid']/elapsed
        write_json(folder/f'block-{block}.json',result);blocks.append(result)
    fanout=[]
    for n in (1,5,20):
        # Repeat questions over an identical state: serial dispatch cost, not native batching.
        start=time.perf_counter();preds=[(await adapter.predict(pack[0],cap)).model_dump() for i in range(n)]
        fanout.append({'questions':n,'native_batch':False,'mode':'serial adapter fanout','elapsed_ms':(time.perf_counter()-start)*1000,'valid':sum(p['status']=='ok' for p in preds)})
    result={'blocks':[{k:v for k,v in b.items() if k!='predictions'} for b in blocks],'fanout':fanout,'unsupported_concurrency':[4,16],'reason':'Reference stdio worker supports one in-flight request; concurrency scaling is not inferred.'}
    write_json(folder/'summary.json',result);return result
