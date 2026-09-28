from __future__ import annotations
import asyncio
import html
import io
import json
import os
import secrets
import time
import zipfile
from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException,Request,Query
from fastapi.responses import FileResponse,StreamingResponse,HTMLResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from arena.config import ROOT,RUNS,DATA
from arena.contracts import RunRequest
from arena.controller import Controller,TERMINAL
from arena.prepare import prepare_model
from arena.registry import REGISTRY

controller=Controller();TOKEN=secrets.token_urlsafe(32)

@asynccontextmanager
async def lifespan(app):
    await controller.recover()
    yield
    for event in controller.cancels.values():event.set()
    pending=[t for t in controller.tasks.values() if not t.done()]
    if pending:
        try:await asyncio.wait_for(asyncio.gather(*pending,return_exceptions=True),30)
        except asyncio.TimeoutError:pass

app=FastAPI(title="Jev Arena",version="0.1.0",lifespan=lifespan)

@app.middleware("http")
async def local_boundary(request:Request,call_next):
    host=request.headers.get("host","").split(":")[0]
    if host not in ("127.0.0.1","localhost","testserver"):
        return JSONResponse({"detail":"Arena accepts loopback requests only"},status_code=403)
    if request.method not in ("GET","HEAD","OPTIONS"):
        origin=request.headers.get("origin")
        if origin and origin not in ("http://127.0.0.1:5173","http://localhost:5173","http://127.0.0.1:8787","http://localhost:8787"):
            return JSONResponse({"detail":"Cross-origin mutation rejected"},status_code=403)
        if request.headers.get("x-arena-token")!=TOKEN:return JSONResponse({"detail":"Local session token required"},status_code=403)
    response=await call_next(request)
    response.headers["X-Content-Type-Options"]="nosniff"
    response.headers["Referrer-Policy"]="no-referrer"
    return response

@app.get("/api/session")
async def session():return {"token":TOKEN,"version":"0.1.0"}

@app.get("/api/readiness")
async def readiness():return await controller.readiness()

@app.get("/api/runs")
async def runs():return controller.store.runs()

@app.get("/api/abcd/cases")
async def abcd_cases(condition:str=Query("",pattern="^(|full_handbook|retrieved_policy|controlled_stress)$"),
                     task:str=Query("",pattern="^(|route|action|synthetic_action)$"),
                     conversation:int|None=Query(None,ge=0),offset:int=Query(0,ge=0),limit:int=Query(50,ge=1,le=100)):
    from arena.abcd_explorer import case_index
    try:return await asyncio.to_thread(case_index,condition,task,conversation,offset,limit)
    except FileNotFoundError as e:raise HTTPException(404,str(e))

@app.get("/api/abcd/cases/{case_id}")
async def abcd_case(case_id:str):
    from arena.abcd_explorer import case_detail
    try:return await asyncio.to_thread(case_detail,case_id)
    except FileNotFoundError as e:raise HTTPException(404,str(e))
    except KeyError:raise HTTPException(404,"ABCD case not found")

@app.post("/api/runs")
async def start(req:RunRequest):
    try:return {"id":await controller.start(req)}
    except ValueError as e:raise HTTPException(409,str(e))

def require_run(rid):
    run=controller.store.run(rid)
    if not run:raise HTTPException(404,"Run not found")
    return run

@app.get("/api/runs/{rid}")
async def run(rid:str):return require_run(rid)

@app.get("/api/runs/{rid}/results")
async def results(rid:str):
    run=require_run(rid);path=RUNS/rid/"results.json"
    if run["status"]=="complete" and path.exists():
        result=json.loads(path.read_text(encoding="utf-8"));result["status"]=run["status"];return result
    return await asyncio.to_thread(controller.results,rid)

@app.get("/api/runs/{rid}/cases")
async def cases(rid:str,model:str|None=None,pack:str|None=None,offset:int=0,limit:int=100):
    require_run(rid)
    values=controller.cases(rid)
    if pack:values=[c for c in values if c.pack==pack]
    subset=values[max(0,offset):max(0,offset)+min(200,max(1,limit))];ids={c.id for c in subset}
    return {"total":len(values),"cases":[c.model_dump() for c in subset],"predictions":[p for p in controller.store.predictions(rid,model) if p["case_id"] in ids]}

@app.get("/api/runs/{rid}/events")
async def events(rid:str,request:Request,after:int=0):
    require_run(rid)
    try:after=max(after,int(request.headers.get("last-event-id","0")))
    except ValueError:raise HTTPException(400,"Invalid event cursor")
    async def stream():
        cursor=after
        while not await request.is_disconnected():
            rows=controller.store.events(rid,cursor)
            for row in rows:
                cursor=row["id"]
                yield f"id: {cursor}\nevent: arena\ndata: {json.dumps(row)}\n\n"
            if require_run(rid)["status"] in TERMINAL and not rows:yield "event: done\ndata: {}\n\n";break
            if not rows:yield ": heartbeat\n\n"
            await asyncio.sleep(.5)
    return StreamingResponse(stream(),media_type="text/event-stream",headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@app.get("/api/runs/{rid}/timeline")
async def timeline(rid:str):
    require_run(rid);out=[];cursor=0
    while rows:=controller.store.events(rid,cursor):out.extend(rows);cursor=rows[-1]["id"]
    return out

@app.post("/api/runs/{rid}/cancel")
async def cancel(rid:str):require_run(rid);controller.cancel(rid);return {"ok":True}

@app.post("/api/runs/{rid}/resume")
async def resume(rid:str):
    try:await controller.resume(rid);return {"ok":True}
    except ValueError as e:raise HTTPException(409,str(e))

@app.post("/api/setup/prepare")
async def prepare(request:Request):
    data=await request.json();models=data.get("model_ids",[])
    if not isinstance(models,list) or not models or any(m not in REGISTRY for m in models):raise HTTPException(400,"Choose registered entrants")
    if controller.setup_task and not controller.setup_task.done():raise HTTPException(409,"Preparation already running")
    if any(r['status'] not in TERMINAL for r in controller.store.runs()):raise HTTPException(409,"Wait for the active run before changing runtime files")
    async def work():
        def progress(message):controller.store.set_setting("setup",{"status":"preparing","message":message,"updated":time.time()})
        try:
            from arena.setup import prepare
            await asyncio.to_thread(prepare,models,progress)
            controller.store.set_setting("setup",{"status":"complete","message":"Selected models, GPU runtimes and datasets prepared."})
        except Exception as e:controller.store.set_setting("setup",{"status":"failed","message":str(e)})
    controller.setup_task=asyncio.create_task(work());return {"ok":True}

@app.post("/api/setup/judge-check")
async def judge_check():
    from arena.judge import smoke_judge
    try:return await smoke_judge()
    except Exception as e:raise HTTPException(409,str(e))

@app.get("/api/runs/{rid}/export")
async def export(rid:str):
    run=require_run(rid)
    result=await asyncio.to_thread(controller.results,rid,True)
    from arena.report import public_report,standalone,license_notices
    payload=public_report(result,run)
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("results.json",json.dumps(payload,indent=2))
        z.writestr('report.html',standalone(payload))
        z.writestr('LICENSES.txt',license_notices())
        notes='Report-time methodology notes. These explain the current viewer and known reference cautions; the original source-snapshot.zip remains frozen to the run.\n\n'
        notes+='\n\n'.join((ROOT/name).read_text(encoding='utf-8') for name in ('docs/IMPLEMENTATION.md','docs/REFERENCE-CAUTIONS.md'))
        z.writestr('METHOD-NOTES.md',notes)
        z.writestr('reference-cautions.json',(ROOT/'docs/reference-cautions.json').read_text(encoding='utf-8'))
        source=RUNS/rid/'source-snapshot.zip'
        if source.exists():z.write(source,'source-snapshot.zip')
        z.writestr("predictions.jsonl","\n".join(json.dumps({k:v for k,v in p.items() if k not in ("raw","error")}) for p in controller.store.predictions(rid)))
        z.writestr("README.txt","Measured Jev Arena results. Inspect limitations before making claims. Raw credentials, logs, user paths and third-party dataset text are excluded. Full local evidence remains in the originating machine's private run directory.")
    return StreamingResponse(iter([buffer.getvalue()]),media_type="application/zip",headers={"Content-Disposition":f'attachment; filename="jev-arena-{rid}.zip"'})

@app.get('/api/runs/{rid}/report')
async def portable_report(rid:str):
    from arena.report import public_report,standalone
    run=require_run(rid)
    result=await asyncio.to_thread(controller.results,rid,True)
    payload=public_report(result,run)
    return HTMLResponse(standalone(payload),headers={'Cache-Control':'no-store'})

if (ROOT/"dist"/"assets").exists():app.mount("/assets",StaticFiles(directory=ROOT/"dist"/"assets"),name="assets")

@app.get("/{path:path}")
async def index(path:str):
    if path.startswith("api/"):raise HTTPException(404,"Unknown API endpoint")
    if (ROOT/"dist"/"index.html").exists():return FileResponse(ROOT/"dist"/"index.html")
    return HTMLResponse("Frontend is running at <a href='http://127.0.0.1:5173'>localhost:5173</a> during development.")
