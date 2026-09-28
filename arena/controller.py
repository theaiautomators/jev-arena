from __future__ import annotations
import asyncio
import json
import os
import random
import time
import uuid
import zipfile
from collections import defaultdict
from dataclasses import asdict
from arena import judge
from arena.adapters import Adapter, IMAGE, IMAGES, IMPLEMENTED
from arena.config import DATA, ROOT, RUNS, digest, write_json
from arena.contracts import Case, RunRequest
from arena.hardware import hardware,command
from arena.prepare import model_info
from arena.registry import REGISTRY, public_registry
from arena.scoring import summarize,paired
from arena.store import Store
from arena.suites import suite,inventory
from filelock import FileLock, Timeout as LockTimeout
from arena.episodes import run_episodes
from arena.performance import measure
from arena.audit import stratified_ids, disagreement_ids

TERMINAL={"complete","cancelled","failed","judging_incomplete","partial","interrupted"}

def implementation_hash():
    return digest({p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for base in ('arena','workers') for p in sorted((ROOT/base).glob('*.py'))})

async def runtime_fingerprint(ids):
    images={}
    for mid in ids:
        if not REGISTRY[mid].hosted and mid!='uniform':
            name=IMAGES.get(REGISTRY[mid].runtime,IMAGE)
            if name not in images:images[name]=(await asyncio.to_thread(command,['docker','image','inspect',name,'--format','{{.Id}}']))['text']
    return {'implementation':implementation_hash(),'models':{mid:digest(model_info(mid)) for mid in ids},'images':images}

class Controller:
    def __init__(self,store=None):
        self.store=store or Store();self.tasks={};self.cancels={};self.lease=asyncio.Lock();self.setup_task=None

    async def recover(self):
        # A previous process cannot be trusted to have completed its last stage.
        probe=FileLock(DATA/"gpu.lock")
        try:probe.acquire(timeout=0)
        except LockTimeout:return
        probe.release()
        for run in self.store.runs():
            if run["status"] not in TERMINAL:self.store.status(run["id"],"interrupted","Controller restarted. Resume keeps completed predictions and redoes unfinished work.")

    async def readiness(self):
        hw,docker,cli=await asyncio.gather(asyncio.to_thread(hardware),asyncio.to_thread(command,["docker","image","inspect",IMAGE,"--format","{{.Id}}"]),asyncio.to_thread(judge.preflight))
        models=[]
        images={IMAGE:docker["ok"]}
        for image_name in IMAGES.values():
            images[image_name]=(await asyncio.to_thread(command,["docker","image","inspect",image_name,"--format","{{.Id}}"]))["ok"]
        for e in public_registry():
            info=model_info(e["id"])
            ready=e["id"]=="uniform" or (e["hosted"] and bool(os.environ.get("TYPESAFE_API_KEY"))) or (e["runtime"] in IMPLEMENTED and bool(info and info.get("complete")) and images.get(IMAGES.get(e["runtime"],IMAGE),False) and bool(hw["gpu"]))
            reason=None if ready else "Add your TypeSafe key" if e["hosted"] else "Native integration pending" if e["runtime"] not in IMPLEMENTED else "Prepare model weights" if not info else "GPU worker unavailable"
            models.append({**e,"ready":ready,"reason":reason,"prepared":bool(info),"resolved_revision":info.get("resolved_revision") if info else None})
        proof=DATA/"judge-smoke"/"metadata.json"
        if proof.exists():
            meta=json.loads(proof.read_text(encoding="utf-8"));cli["smoke_passed"]=meta.get("exit_code")==0 and not meta.get("tool_events");cli["observed_model"]=meta.get("observed_model")
        control=DATA/'judge-controls'/judge.VERSION/'report.json'
        if control.exists():cli['controls']={k:v for k,v in json.loads(control.read_text(encoding="utf-8")).items() if k!='results'}
        active=next((r['id'] for r in self.store.runs() if r['status'] not in TERMINAL),None)
        return {"hardware":hw,"models":models,"docker_ready":docker["ok"],"judge":cli,"suites":inventory(),"setup":self.store.setting("setup",{}),"active_run":active}

    async def start(self,request:RunRequest):
        if len(set(request.model_ids))!=len(request.model_ids):raise ValueError("Duplicate entrants")
        if any(x not in REGISTRY for x in request.model_ids):raise ValueError("Unknown entrant")
        existing=next((r for r in self.store.runs() if r["request"].get("idempotency_key")==request.idempotency_key),None)
        if existing:
            if existing["request"]!=request.model_dump():raise ValueError("Idempotency key reused with different settings")
            return existing["id"]
        if any(not t.done() for t in self.tasks.values()):raise ValueError("Another run owns the GPU. Cancel or wait for it first.")
        probe=FileLock(DATA/'gpu.lock')
        try:probe.acquire(timeout=0)
        except LockTimeout:raise ValueError('Another Arena process owns the GPU. Wait for its run to finish.')
        else:probe.release()
        cases=suite(request.preset)
        ready=await self.readiness();lookup={m["id"]:m for m in ready["models"]}
        missing=[lookup[m]["name"]+": "+lookup[m]["reason"] for m in request.model_ids if not lookup[m]["ready"]]
        if missing:raise ValueError("Setup needed: "+"; ".join(missing))
        if request.judge and not ready["judge"]["ready"]:raise ValueError(ready["judge"]["reason"])
        rid=time.strftime("%Y%m%d-%H%M%S")+"-"+uuid.uuid4().hex[:6]
        records=[c.model_dump() for c in cases]
        order=list(request.model_ids);random.Random(request.seed).shuffle(order)
        manifest={"version":"arena-v1","created":time.time(),"request":request.model_dump(),"case_count":len(cases),"case_sha256":digest(records),"hardware":ready["hardware"],"entrants":[lookup[m] for m in request.model_ids],"order":order,"judge":{"requested_model":judge.MODEL,"transport":"Codex CLI / ChatGPT login","rubric":judge.VERSION},"artifact_kind":"measured","fresh_labels":"formal executable-policy fixtures; no human semantic audit claimed","protocol_sha256":digest((ROOT/"EVALUATION.md").read_bytes()),"source_sha256":digest({p.relative_to(ROOT).as_posix():digest(p.read_bytes()) for p in sorted((ROOT/"arena").glob("*.py"))})}
        manifest['implemented_profile_sha256']=digest((ROOT/'docs'/'IMPLEMENTATION.md').read_bytes())
        manifest['version']='arena-v2'
        manifest['fixture_version']='formal-v2'
        manifest['judge']['audit_ids']=stratified_ids(cases,request.judge_audit_cases,request.seed)
        manifest['judge']['disagreement_rule']='hashed-distinct-selected-labels-excluding-uniform-v1'
        manifest['judge']['disagreement_limit']=request.judge_disagreement_cases
        manifest['runtime_fingerprint']=await runtime_fingerprint(request.model_ids)
        manifest['judge']['controls']=ready['judge'].get('controls')
        manifest['declared_option_cohort']=[c.id for c in cases if all(len(c.question.labels)<=REGISTRY[mid].max_options for mid in request.model_ids)]
        self.store.create_run(rid,request.model_dump(),manifest)
        folder=RUNS/rid;folder.mkdir(parents=True)
        write_json(folder/"manifest.json",manifest)
        with zipfile.ZipFile(folder/'source-snapshot.zip','w',zipfile.ZIP_DEFLATED) as archive:
            for base in ('arena','workers'):
                for path in sorted((ROOT/base).glob('*')):
                    if path.is_file() and (path.suffix=='.py' or path.name.startswith('Dockerfile')):archive.write(path,path.relative_to(ROOT).as_posix())
            for name in ('uv.lock','package-lock.json','sources.lock.json','EVALUATION.md','docs/IMPLEMENTATION.md','docs/VIDEO-EVALUATION-V2.md','docs/REFERENCE-CAUTIONS.md','docs/reference-cautions.json','LICENSE','THIRD-PARTY-LICENSES.txt'):
                path=ROOT/name
                if path.exists():archive.write(path,name)
        (folder/"cases.jsonl").write_text("\n".join(json.dumps(c,ensure_ascii=False) for c in records)+"\n",encoding="utf-8")
        self.cancels[rid]=asyncio.Event();self.tasks[rid]=asyncio.create_task(self.execute(rid,cases))
        return rid

    def cases(self,rid):
        path=RUNS/rid/"cases.jsonl"
        return [Case.model_validate_json(s) for s in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []

    async def execute(self,rid,cases):
        lock=FileLock(DATA/"gpu.lock")
        try:lock.acquire(timeout=0)
        except LockTimeout:
            self.store.status(rid,"failed","Another Arena controller owns the GPU lease.")
            return
        async def watch_cancel():
            while True:
                if self.store.setting('cancel:'+rid,False):self.cancels[rid].set();return
                await asyncio.sleep(.5)
        watcher=asyncio.create_task(watch_cancel())
        try:await self._execute(rid,cases)
        finally:
            watcher.cancel()
            lock.release()

    async def _execute(self,rid,cases):
        async with self.lease:
            run=self.store.run(rid);req=RunRequest(**run["request"]);cancel=self.cancels[rid];folder=RUNS/rid
            adapter=None
            try:
                self.store.status(rid,"preflight")
                # Resume after a hard controller exit may leave a Docker worker alive.
                # The GPU file lock is held here; verify the exact name AND ownership label.
                for mid in req.model_ids:
                    if REGISTRY[mid].hosted or mid=='uniform':continue
                    name='jev-arena-'+rid+'-'+mid
                    inspect=await asyncio.to_thread(command,['docker','inspect',name,'--format','{{ index .Config.Labels "app" }}'])
                    if inspect['ok']:
                        if inspect['text']!='jev-arena':raise RuntimeError('Container name collision with a worker not owned by Arena')
                        await asyncio.to_thread(command,['docker','stop','--time','5',name],15)
                        alive=await asyncio.to_thread(command,['docker','inspect',name,'--format','{{.State.Running}}'])
                        if alive['ok'] and alive['text']=='true':raise RuntimeError('Orphaned Arena worker did not stop')
                        self.store.event(rid,'recovered_worker',{'model_id':mid,'container':name})
                for mid in run["manifest"]["order"]:
                    if cancel.is_set():raise asyncio.CancelledError()
                    completed={p["case_id"] for p in self.store.predictions(rid,mid)}
                    pending=[c for c in cases if c.id not in completed]
                    worker_folder=folder/'workers'/mid
                    needs_perf=req.preset=='full' and not (worker_folder/'performance'/'summary.json').exists()
                    needs_episodes=req.preset in ('demo','full') and not (worker_folder/'episodes.json').exists()
                    if not pending and not needs_perf and not needs_episodes and self.store.setting(f'done:{rid}:{mid}',False):continue
                    self.store.event(rid,"model",{"model_id":mid,"name":REGISTRY[mid].name,"completed":len(completed),"total":len(cases)})
                    self.store.status(rid,"loading")
                    adapter=Adapter(mid,folder/"workers"/mid,cancel)
                    try:
                        await adapter.load();write_json(adapter.folder/"load.json",adapter.meta)
                        self.store.event(rid,"loaded",{"model_id":mid,**adapter.meta})
                        self.store.status(rid,"warming")
                        warm=[]
                        for i in range(10):
                            pred=await adapter.predict((pending or cases)[i%len(pending or cases)],req.paid_cap_usd)
                            warm.append(pred.model_dump())
                            if pred.status in ('timeout','transport_error'):raise RuntimeError(f"{REGISTRY[mid].name} failed warmup: {pred.error}")
                        write_json(adapter.folder/"warmup.json",warm)
                        if not any(p['status']=='ok' for p in warm):raise RuntimeError('No valid warmup result. Inspect saved warmup evidence before measuring this runtime.')
                        self.store.status(rid,"evaluating")
                        for i,case in enumerate(pending):
                            if cancel.is_set():raise asyncio.CancelledError()
                            pred=await adapter.predict(case,req.paid_cap_usd)
                            self.store.prediction(rid,pred)
                            self.store.event(rid,"prediction",{"model_id":mid,"case_id":case.id,"status":pred.status,"selected":pred.selected,"request_ms":pred.request_ms,"completed":len(completed)+i+1,"total":len(cases)})
                            if adapter.dead:raise RuntimeError("Worker became unavailable; remaining cases were not attempted")
                        if needs_perf:
                            self.store.status(rid,"performance")
                            await measure(adapter,cases,adapter.folder/"performance",req.paid_cap_usd)
                        if needs_episodes:
                            self.store.status(rid,"episodes")
                            episodes=await run_episodes(adapter,40 if req.preset=="full" else 4,req.paid_cap_usd,on_progress=lambda row:self.store.event(rid,"episode",{k:v for k,v in row.items() if k!='trace'}))
                            if req.preset=='full':
                                episodes+=await run_episodes(adapter,40,req.paid_cap_usd,deadline_ms=500,on_progress=lambda row:self.store.event(rid,'episode',{k:v for k,v in row.items() if k!='trace'}))
                            write_json(adapter.folder/"episodes.json",episodes)
                        self.store.event(rid,"model_complete",{"model_id":mid,"cost_usd":adapter.cost,"cost_reserved_usd":adapter.reserved})
                    finally:
                        self.store.status(rid,"unloading")
                        cleanup=await asyncio.shield(adapter.unload())
                        write_json(adapter.folder/"cleanup.json",cleanup)
                        self.store.event(rid,"unloaded",{"model_id":mid,**cleanup});adapter=None
                        if cleanup.get('memory_within_baseline') is False:raise RuntimeError('GPU memory did not return within the recorded baseline. Inspect other GPU users before resuming.')
                    if req.preset=="full" and not REGISTRY[mid].hosted and mid!="uniform":
                        for cycle in (2,3):
                            if (worker_folder/f'cycle-{cycle}-cleanup.json').exists():continue
                            probe=Adapter(mid,folder/"workers"/mid,cancel)
                            try:
                                self.store.status(rid,"loading")
                                await probe.load()
                                pred=await probe.predict(cases[0],req.paid_cap_usd)
                                write_json(probe.folder/f"cycle-{cycle}.json",{"load":probe.meta,"first_inference":pred.model_dump()})
                            finally:
                                cleaned=await asyncio.shield(probe.unload())
                                write_json(probe.folder/f"cycle-{cycle}-cleanup.json",cleaned)
                                if cleaned.get('memory_within_baseline') is False:raise RuntimeError('GPU memory cleanup verification failed')
                    self.store.set_setting(f'done:{rid}:{mid}',True)
                if req.judge:
                    self.store.status(rid,"judging")
                    await self.judge_run(rid,cases,cancel)
                self.store.status(rid,"verifying")
                result=await asyncio.to_thread(self.results,rid,True)
                expected=len(cases)*len(req.model_ids);done=len(self.store.predictions(rid))
                status="complete" if done==expected else "partial"
                result['status']=status
                write_json(folder/"results.json",result)
                self.store.status(rid,status)
                self.export_evidence(rid)
            except asyncio.CancelledError:
                self.store.status(rid,"cancelled","Run cancelled. Completed predictions remain available.");self.export_evidence(rid)
            except judge.JudgePaused as e:self.store.status(rid,"judging_incomplete",str(e));self.export_evidence(rid)
            except Exception as e:self.store.status(rid,"failed",str(e));self.export_evidence(rid)

    async def judge_run(self,rid,cases,cancel):
        lookup={c.id:c for c in cases};groups=defaultdict(list)
        predictions=self.store.predictions(rid)
        for p in predictions:
            if p['status'] in ('ok','invalid') and p['selected'] in lookup[p['case_id']].question.labels:
                groups[(p["case_id"],p["selected"])].append(p["model_id"])
        run=self.store.run(rid);req=RunRequest(**run['request'])
        representative=run['manifest']['judge'].get('audit_ids',stratified_ids(cases,req.judge_audit_cases,req.seed))
        extra=disagreement_ids(cases,predictions,set(representative),req.judge_disagreement_cases,req.seed)
        audit_ids=set(representative)|set(extra)
        write_json(RUNS/rid/'audit-selection.json',{'representative_ids':representative,'disagreement_ids':extra,'selection_note':'Representative IDs frozen before inference. Extra disagreements sampled by a frozen hash rule without consulting gold. Semantic audit includes selected labels with invalid probabilities; primary metrics remain unchanged.'})
        jobs=[]
        for (cid,answer),models in groups.items():
            c=lookup[cid]
            if c.label_status not in ("provisional","audited") and cid not in audit_ids:continue
            jid=digest([cid,answer,judge.VERSION])[:20]
            jobs.append((jid,{"case_id":cid,"question_id":c.question.id,"state":c.state,"question":c.question.text,"rubric":c.question.rubric,"allowed_answers":c.question.labels,"proposed_answer":answer},models))
        old={j["job_id"]:j for j in self.store.judge_jobs(rid)}
        pending=[j for j in jobs if old.get(j[0],{}).get("status")!="complete"]
        # A batch may not contain two different answers for the same case ID.
        while pending:
            batch=[];seen=set()
            for j in list(pending):
                if j[1]["case_id"] not in seen:
                    batch.append(j);seen.add(j[1]["case_id"]);pending.remove(j)
                if len(batch)==8:break
            items=[j[1] for j in batch];batchid=digest(items)[:16]
            for jid,item,models in batch:self.store.judge_job(rid,jid,"running",{"models":models,"item":item})
            result=None
            for attempt in (1,2):
                try:
                    result=await judge.grade(items,RUNS/rid/"judge"/batchid/f"attempt-{attempt}",cancel);break
                except judge.JudgePaused:raise
                except asyncio.CancelledError:raise
                except Exception:
                    if attempt==2:raise judge.JudgePaused("Judge batch failed verification twice; inspect evidence and resume judging.")
                    await asyncio.sleep(1)
            grades={g["case_id"]:g for g in result["grades"]}
            for jid,item,models in batch:self.store.judge_job(rid,jid,"complete",{"models":models,"item":item,"grade":grades[item["case_id"]],"metadata":result["metadata"],"role":"semantic_grade" if lookup[item["case_id"]].label_status in ("provisional","audited") else "reference_audit"})
            self.store.event(rid,"judge_progress",{"complete":len(jobs)-len(pending),"total":len(jobs)})

    def results(self,rid,ci=False):
        run=self.store.run(rid);cases=self.cases(rid);rows=self.store.predictions(rid);by_model=defaultdict(list)
        for p in rows:by_model[p["model_id"]].append(p)
        entrants=[]
        for mid in run["request"]["model_ids"]:
            entrants.append({"id":mid,"name":REGISTRY[mid].name,"hosted":REGISTRY[mid].hosted,"metrics":summarize(cases,by_model[mid],ci)})
        # Common cohort uses observed hard capability exclusions, displayed explicitly.
        unsupported={p["case_id"] for p in rows if p["status"]=="unsupported"}
        matched=[c for c in cases if c.id not in unsupported]
        for e in entrants:e["matched"]=summarize(matched,by_model[e["id"]],False)
        comparisons=[]
        if ci:
            for ref in ("jev","qwen"):
                if ref in by_model:
                    for mid in by_model:
                        if mid!=ref:comparisons.append({"model":mid,"reference":ref,**paired(cases,by_model[mid],by_model[ref])})
        performance={};episodes=[]
        for mid in run["request"]["model_ids"]:
            perf=RUNS/rid/"workers"/mid/"performance"/"summary.json"
            ep=RUNS/rid/"workers"/mid/"episodes.json"
            if perf.exists():performance[mid]=json.loads(perf.read_text(encoding="utf-8"))
            if ep.exists():episodes.extend(json.loads(ep.read_text(encoding="utf-8")))
        return {"run_id":rid,"status":run["status"],"kind":"measured","preset":run["request"]["preset"],"case_count":len(cases),"matched_count":len(matched),"matched_basis":"Observed hard-limit intersection. Tokenizer context exclusions are observed; only option limits were frozen before execution.","entrants":entrants,"comparisons":comparisons,"judge_jobs":self.store.judge_jobs(rid),"manifest":run["manifest"],"performance":performance,"episodes":episodes,"performance_complete":len(performance)==len(entrants),"publication_ready":False,"limitations":["Main accuracy excludes teacher and provisional labels; teacher agreement is separate.","Quality-request latency; dedicated performance blocks are reported separately.","Formal fresh fixtures share policy templates across splits; they do not establish broad semantic generalization.","Human audit required before headline claims. Paired intervals are descriptive; no corrected significance claims."]}

    def export_evidence(self,rid):
        folder=RUNS/rid
        for name,values in (("predictions",self.store.predictions(rid)),("judge-jobs",self.store.judge_jobs(rid))):
            (folder/f"{name}.jsonl").write_text("\n".join(json.dumps(v,ensure_ascii=False) for v in values)+"\n",encoding="utf-8")
        events=[];after=0
        while batch:=self.store.events(rid,after):events.extend(batch);after=batch[-1]["id"]
        write_json(folder/"events.json",events)
        write_json(folder/"run.json",self.store.run(rid))

    async def resume(self,rid):
        run=self.store.run(rid)
        if not run:raise ValueError("Run not found")
        if any(not t.done() for t in self.tasks.values()):raise ValueError("Another run is active")
        if run["status"]=="complete":raise ValueError("Run already complete")
        # Refuse altered suite files on resume.
        cases=self.cases(rid)
        if digest([c.model_dump() for c in cases])!=run["manifest"]["case_sha256"]:raise ValueError("Frozen case manifest was modified")
        if run['manifest'].get('runtime_fingerprint')!=await runtime_fingerprint(run['request']['model_ids']):raise ValueError('Code, weights or runtime changed since this run. Start a new run to avoid mixing measurements.')
        self.store.set_setting('cancel:'+rid,False)
        self.cancels[rid]=asyncio.Event();self.tasks[rid]=asyncio.create_task(self.execute(rid,cases))

    def cancel(self,rid):
        self.store.set_setting("cancel:"+rid,True)
        if rid in self.cancels:self.cancels[rid].set()
