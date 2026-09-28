from __future__ import annotations
import asyncio
import platform
import shutil
import subprocess
from arena.config import DATA

def command(args,timeout=15):
    try:
        p=subprocess.run(args,capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=timeout,creationflags=subprocess.CREATE_NO_WINDOW if platform.system()=="Windows" else 0)
        return {"ok":p.returncode==0,"text":(p.stdout if p.returncode==0 else p.stderr).strip()[:2000]}
    except (OSError,subprocess.TimeoutExpired) as e:return {"ok":False,"text":str(e)}

def hardware():
    gpu=command(["nvidia-smi","--query-gpu=name,memory.total,memory.used,temperature.gpu,power.draw,driver_version","--format=csv,noheader,nounits"])
    parsed=None
    if gpu["ok"]:
        parts=gpu["text"].splitlines()[0].split(", ")
        if len(parts)==6:
            def num(v):
                try:return float(v)
                except ValueError:return None
            parsed=dict(zip(["name","memory_total_mb","memory_used_mb","temperature_c","power_w","driver"],[parts[0],*map(num,parts[1:5]),parts[5]]))
    disk=shutil.disk_usage(DATA)
    return {"gpu":parsed,"gpu_error":None if gpu["ok"] else gpu["text"],"platform":platform.platform(),"python":platform.python_version(),"disk_free_gb":round(disk.free/2**30,1)}

async def sample_memory():
    info=await asyncio.to_thread(hardware)
    return info.get("gpu",{}).get("memory_used_mb") if info.get("gpu") else None
