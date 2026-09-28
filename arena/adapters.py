from __future__ import annotations
import asyncio
import json
import os
import time
from pathlib import Path
import httpx
from arena.config import MODELS, ROOT, digest
from arena.contracts import Case, Prediction
from arena.registry import REGISTRY
from arena.scoring import validate_prediction
from arena.hardware import command,sample_memory
from arena.prepare import model_info
from arena.wire import native_question,normalize_answer

IMAGE="jev-arena-worker:0.1"
IMAGES={"clm":"jev-arena-clm:0.1","winnow":"jev-arena-winnow-bridge:0.1"}
IMPLEMENTED={"laya","jevk5","decider","nli","qwen","semif","nimble","clm","winnow"}

def question(case):
    return native_question(case.question.model_dump())

def native_answer(answer,case):
    return normalize_answer(answer,case.question.model_dump())

class Adapter:
    def __init__(self,model_id,folder,cancel):
        self.entrant=REGISTRY[model_id];self.id=model_id;self.folder=Path(folder);self.cancel=cancel;self.meta={};self.proc=None;self.stderr_task=None;self.dead=False
        self.name="jev-arena-"+self.folder.parent.parent.name+"-"+model_id
        self.client=None;self.cost=0.;self.reserved=0.;self.calls=0
        ledger=self.folder/'cost-ledger.json'
        if ledger.exists():
            saved=json.loads(ledger.read_text(encoding="utf-8"));self.cost=saved['actual_usd'];self.reserved=saved['reserved_usd']

    async def load(self):
        self.folder.mkdir(parents=True,exist_ok=True)
        if self.id=="uniform":self.meta={"runtime":"statistical","revision":"arena-v1"};return
        if self.entrant.hosted:
            self.client=httpx.AsyncClient(timeout=60,follow_redirects=False)
            self.meta={"revision":self.entrant.revision,"endpoint":"https://api.typesafe.ai/v1/systemone"};return
        if self.entrant.runtime not in IMPLEMENTED:raise RuntimeError(f"{self.entrant.name}: native worker integration pending")
        info=model_info(self.id)
        if not info or not info.get("complete"):raise RuntimeError("Model weights need preparation")
        self.baseline=await sample_memory()
        cmd=["docker","run","--rm","-i","--name",self.name,"--label","app=jev-arena","--gpus","all","--network","none","--read-only","--cap-drop","ALL","--security-opt","no-new-privileges","--tmpfs","/tmp:rw,exec,size=4g","--shm-size","1g","-e","HF_HUB_OFFLINE=1","-e","TRANSFORMERS_OFFLINE=1","-e","HF_HOME=/tmp/hf","-e","TRITON_CACHE_DIR=/tmp/triton","-e","ARENA_RUNTIME="+self.entrant.runtime,"-e","ARENA_CONTEXT="+str(self.entrant.context),"-e","ARENA_SUBFOLDER="+self.entrant.subfolder,"--mount",f"type=bind,source={MODELS/self.id/'weights'},target=/weights/model,readonly",IMAGE]
        cmd[-2]=f"type=bind,source={MODELS/info.get('weights_model',self.id)/'weights'},target=/weights/model,readonly"
        cmd[-1]=IMAGES.get(self.entrant.runtime,IMAGE)
        cmd[-1:-1]=["-e","ARENA_REVISION="+info["resolved_revision"]]
        cmd[-1:-1]=['-e','HOME=/tmp','-e','XDG_CACHE_HOME=/tmp/cache','-e','VLLM_CACHE_ROOT=/tmp/vllm','-e','FLASHINFER_WORKSPACE_BASE=/tmp/flashinfer']
        if self.entrant.runtime=='clm':
            cmd[-1:-1]=['-e','VLLM_BATCH_INVARIANT=1']
        self.proc=await asyncio.create_subprocess_exec(*cmd,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE,limit=4*1024*1024)
        async def log():
            with (self.folder/"worker.log").open("wb") as f:
                while data:=await self.proc.stderr.read(4096):f.write(data);f.flush()
        self.stderr_task=asyncio.create_task(log())
        line=await self._line(600)
        response=json.loads(line)
        if not response.get("ready"):raise RuntimeError(response.get("error","Worker failed to load"))
        image=await asyncio.to_thread(command,["docker","image","inspect",IMAGES.get(self.entrant.runtime,IMAGE),"--format","{{.Id}}"])
        self.meta={**response,"revision":info["resolved_revision"],"weights_manifest_hash":digest(info),"image_id":image["text"] if image["ok"] else None,"isolation":"networkless read-only container; weight mount only"}
        if self.entrant.runtime=='clm':
            self.meta.update(runtime_profile='clm-v2-batch-invariant',batch_invariant=True)

    async def _line(self,timeout):
        task=asyncio.create_task(self.proc.stdout.readline())
        cancelled=asyncio.create_task(self.cancel.wait())
        try:
            done,_=await asyncio.wait({task,cancelled},timeout=timeout,return_when=asyncio.FIRST_COMPLETED)
            if cancelled in done:raise asyncio.CancelledError()
            if task not in done:raise TimeoutError('Worker deadline exceeded')
            line=await task
            if not line:raise RuntimeError("Worker exited; inspect saved worker log")
            return line
        except BaseException:
            task.cancel();self.dead=True;raise
        finally:
            cancelled.cancel()

    async def predict(self,case:Case,cap=5):
        base={"case_id":case.id,"model_id":self.id,"input_hash":digest(case.candidate())}
        if len(case.question.labels)>self.entrant.max_options:return Prediction(**base,status="unsupported",error=f"Native limit: {self.entrant.max_options} options")
        if self.cancel.is_set():raise asyncio.CancelledError()
        start=time.perf_counter()
        try:
            if self.id=="uniform":
                probs={k:1/len(case.question.labels) for k in case.question.labels}
                # Deterministic tie break disclosed; no access to reference labels.
                result={"selected":case.question.labels[0],"probabilities":probs,"probability_source":"native","raw":{"tie_break":"first label"}}
            elif self.entrant.hosted:
                reserve=64000*.042/1e6
                if self.reserved+reserve>cap:raise RuntimeError("Paid cap reached; no further request sent")
                self.reserved+=reserve
                from arena.config import write_json
                write_json(self.folder/'cost-ledger.json',{'actual_usd':self.cost,'reserved_usd':self.reserved})
                body={"model":self.entrant.revision,"state":case.state,"questions":{"decision":question(case)}}
                response=await self.client.post("https://api.typesafe.ai/v1/systemone",json=body,headers={"Authorization":"Bearer "+os.environ.get("TYPESAFE_API_KEY","")})
                if response.status_code!=200:raise RuntimeError(f"TypeSafe returned HTTP {response.status_code}")
                raw=response.json();result={**native_answer(raw["answers"]["decision"],case),"raw":raw,"probability_source":"native"}
                usage=raw.get("usage",{});tokens=usage.get("input_tokens")
                result["input_tokens"]=tokens
                if tokens is not None:
                    actual=tokens*.042/1e6;self.cost+=actual;self.reserved+=actual-reserve
                    write_json(self.folder/'cost-ledger.json',{'actual_usd':self.cost,'reserved_usd':self.reserved})
            else:
                if self.dead:raise RuntimeError("Worker stopped after an earlier transport failure")
                self.proc.stdin.write((json.dumps(case.candidate(),ensure_ascii=False)+"\n").encode());await self.proc.stdin.drain()
                result=json.loads(await self._line(600 if self.calls==0 else 120 if len(case.state)>20000 else 60))
                self.calls+=1
            # Keep native runtime fields in raw; strict normalized schema remains stable.
            fields={k:result[k] for k in ("status","selected","probabilities","probability_source","input_tokens","output_tokens","error") if k in result}
            pred=Prediction(**base,**{"status":"ok",**fields},request_ms=(time.perf_counter()-start)*1000,raw=result,raw_valid=result.get('status','ok')=='ok')
        except asyncio.CancelledError:raise
        except (TimeoutError,httpx.TimeoutException) as e:pred=Prediction(**base,status="timeout",request_ms=(time.perf_counter()-start)*1000,error=str(e))
        except Exception as e:pred=Prediction(**base,status="transport_error",request_ms=(time.perf_counter()-start)*1000,error=str(e)[:1000])
        return validate_prediction(pred,case)

    async def unload(self):
        evidence={"owned_container":self.name,"memory_before_load_mb":getattr(self,"baseline",None)}
        if self.client:await self.client.aclose()
        if self.proc:
            # Stop only this run's explicitly named container; never unrelated GPU users.
            result=await asyncio.to_thread(command,["docker","stop","--time","5",self.name],15)
            try:await asyncio.wait_for(self.proc.wait(),10)
            except asyncio.TimeoutError:self.proc.kill();await self.proc.wait()
            if self.stderr_task:await self.stderr_task
            check=await asyncio.to_thread(command,["docker","inspect",self.name,"--format","{{.State.Running}}"])
            if check["ok"] and check["text"]=="true":raise RuntimeError("Owned worker did not stop; GPU lease retained")
            samples=[]
            for _ in range(3):samples.append(await sample_memory());await asyncio.sleep(.3)
            evidence.update({"container_stopped":True,"memory_after_mb":samples,"memory_within_baseline":all(v is not None and self.baseline is not None and v<=self.baseline+512 for v in samples)})
        return evidence
