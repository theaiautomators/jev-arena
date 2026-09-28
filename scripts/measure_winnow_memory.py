"""Measure Winnow idle GPU footprint without sending inference requests."""
import asyncio, json, statistics, time
from pathlib import Path
from filelock import FileLock
from arena.config import DATA, ROOT, write_json
from arena.adapters import Adapter
from arena.hardware import sample_memory
from scripts.abcd_preflight import configured_adapter

async def main():
    stamp=time.strftime('%Y%m%d-%H%M%S',time.gmtime())
    folder=DATA/'memory-probes'/('winnow-'+stamp)
    folder.mkdir(parents=True,exist_ok=False)
    lock=FileLock(DATA/'gpu.lock')
    lock.acquire(timeout=0)
    results=[]
    try:
        for profile,context in [('v2',8192),('abcd',65536)]:
            work=folder/profile/'workers'/'winnow'
            before=[]
            for _ in range(3):
                before.append(await sample_memory()); await asyncio.sleep(.3)
            cancel=asyncio.Event()
            a=Adapter('winnow',work,cancel) if profile=='v2' else configured_adapter('winnow',work,cancel)
            row={'profile':profile,'context_tokens':context,'before_load_mib':before,'requests_sent':0}
            try:
                await a.load()
                loaded=[]
                for _ in range(5):
                    loaded.append(await sample_memory()); await asyncio.sleep(.5)
                row.update(metadata=a.meta,loaded_device_mib=loaded,idle_device_delta_mib=statistics.median(loaded)-statistics.median(before),measured_at=time.time())
            finally:
                row['cleanup']=await a.unload()
                write_json(work/'measurement.json',row)
            if not row['cleanup'].get('memory_within_baseline',False):raise RuntimeError('Memory did not return to baseline; inspect owned cleanup')
            results.append(row)
            print(json.dumps({'profile':profile,'context':context,'delta_mib':row['idle_device_delta_mib'],'cleanup':True}),flush=True)
        public={'measured_date':time.strftime('%Y-%m-%d',time.gmtime()),'gpu':'NVIDIA GeForce RTX 5090','method':'Median whole-device NVIDIA memory.used after server readiness minus median before loading; five loaded and three baseline samples. Other desktop allocations can fluctuate. Not a process allocator measurement, peak VRAM, or system RAM. No inference requests sent.','profiles':[{k:v for k,v in x.items() if k!='cleanup'} for x in results]}
        write_json(ROOT/'docs/evidence/winnow-memory.json',public)
        write_json(folder/'summary.json',{'results':results})
    finally:lock.release()

if __name__=='__main__':asyncio.run(main())
