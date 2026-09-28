"""Compare Arena's CLM deployment with the upstream HTTP inference path."""
import asyncio
import json
import subprocess
from pathlib import Path

from filelock import FileLock
from arena.adapters import Adapter
from arena.config import DATA, MODELS, ROOT, digest, write_json
from arena.fresh import scenario


async def verify():
    folder=DATA/'video-v2'/'native-clm'
    report_file=folder/'report.json'
    if report_file.exists():
        report=json.loads(report_file.read_text(encoding='utf-8'))
        if not report['passed']:
            raise RuntimeError('Saved CLM native parity check failed')
        return report
    inputs=folder/'inputs';inputs.mkdir(parents=True,exist_ok=True)
    cases=[case for i in range(2) for family in range(6) for case in scenario(family,i,'dev')]
    write_json(inputs/'cases.json',[c.candidate() for c in cases])
    # The container only sees candidate inputs, pinned weights and its output
    # folder. Reference labels stay in the host process.
    with FileLock(DATA/'gpu.lock',timeout=0):
        adapter=Adapter('clm',folder/'workers'/'clm',asyncio.Event())
        predictions=[]
        try:
            await adapter.load()
            write_json(folder/'arena-load.json',adapter.meta)
            for case in cases:
                pred=await adapter.predict(case)
                if pred.status not in ('ok','invalid'):
                    raise RuntimeError('CLM wrapper probe failed: '+str(pred.error))
                predictions.append(pred.model_dump())
            write_json(folder/'arena-predictions.json',predictions)
        finally:
            cleanup=await adapter.unload()
            write_json(folder/'arena-cleanup.json',cleanup)
            if cleanup.get('memory_within_baseline') is False:
                raise RuntimeError('CLM probe cleanup failed')
        output=folder/'native';output.mkdir(exist_ok=True)
        name='jev-arena-v2-native-clm'
        command=['docker','run','--rm','--name',name,'--label','app=jev-arena','--gpus','all','--network','none',
                 '--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,exec,size=4g','--shm-size','1g']
        for key,val in {'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HOME':'/tmp','HF_HOME':'/tmp/hf','XDG_CACHE_HOME':'/tmp/cache','VLLM_CACHE_ROOT':'/tmp/vllm','PYTHONPATH':'/opt/arena','VLLM_BATCH_INVARIANT':'1'}.items():
            command+=['-e',key+'='+val]
        for source,destination,readonly in [(MODELS/'clm'/'weights','/weights/model',True),(inputs,'/inputs',True),
                                           (ROOT/'scripts'/'native_clm_http.py','/code/native_clm_http.py',True),(output,'/out',False)]:
            command+=['--mount',f'type=bind,source={source},target={destination}'+(',readonly' if readonly else '')]
        command+=['--entrypoint','python3','jev-arena-clm:0.1','/code/native_clm_http.py']
        write_json(folder/'invocation.json',{'command':command,'script_sha256':digest((ROOT/'scripts/native_clm_http.py').read_bytes()),'candidate_sha256':digest([c.candidate() for c in cases]),'probability_tolerance':1e-4})
        with (folder/'native-launch.log').open('w',encoding='utf-8') as log:
            try:
                process=await asyncio.create_subprocess_exec(*command,stdout=log,stderr=asyncio.subprocess.STDOUT)
                code=await asyncio.wait_for(process.wait(),600)
            finally:
                # Only this explicitly named verification container is stopped.
                await asyncio.to_thread(subprocess.run,['docker','stop','--time','5',name],capture_output=True,timeout=20)
        if code:
            raise RuntimeError('Native CLM path failed; inspect native-launch.log')
        native={p['case_id']:p for p in json.loads((output/'native-predictions.json').read_text(encoding='utf-8'))}
        deltas=[max(abs(p['probabilities'][key]-native[p['case_id']]['probabilities'][key]) for key in p['probabilities']) for p in predictions]
        agreement=sum(p['selected']==native[p['case_id']]['selected'] for p in predictions)
        report={'cases':len(cases),'selected_agreement':agreement,'max_probability_delta':max(deltas),
                'passed':agreement==len(cases) and max(deltas)<=1e-4,
                'runtime_profile':'clm-v2-batch-invariant',
                'scope':'36 short development-style formal probes; Arena in-process vLLM compared with upstream Engine/Embedder through a native vLLM HTTP server. Same pinned BF16 encoder and trained head, batch-invariant mode enabled, prefix caching disabled. Does not establish task suitability, long-context parity or optimized serving speed.'}
        write_json(report_file,report)
        if not report['passed']:
            raise RuntimeError('CLM native numerical parity failed; inspect report.json')
        return report


if __name__=='__main__':
    print(json.dumps(asyncio.run(verify()),indent=2))
