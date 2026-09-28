from __future__ import annotations
import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from arena.config import DATA

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, key TEXT UNIQUE, created REAL, updated REAL, status TEXT, request TEXT, manifest TEXT, error TEXT);
CREATE TABLE IF NOT EXISTS predictions(run_id TEXT, model_id TEXT, case_id TEXT, data TEXT, PRIMARY KEY(run_id,model_id,case_id));
CREATE INDEX IF NOT EXISTS prediction_case ON predictions(run_id,case_id,model_id);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT, time REAL, kind TEXT, data TEXT);
CREATE INDEX IF NOT EXISTS event_run ON events(run_id,id);
CREATE TABLE IF NOT EXISTS judge_jobs(run_id TEXT, job_id TEXT, status TEXT, data TEXT, PRIMARY KEY(run_id,job_id));
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
CREATE TABLE IF NOT EXISTS attempts(run_id TEXT, model_id TEXT, case_id TEXT, attempt INTEGER, data TEXT, PRIMARY KEY(run_id,model_id,case_id,attempt));
"""

class Store:
    def __init__(self,path: Path | str = DATA / "arena.sqlite3"):
        self.path=str(path)
        with self.connect() as db: db.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path, timeout=30)
        db.row_factory=sqlite3.Row
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally: db.close()

    def create_run(self, rid, request, manifest):
        with self.connect() as db:
            old=db.execute("SELECT id, request FROM runs WHERE key=?",(request["idempotency_key"],)).fetchone()
            if old:
                if json.loads(old["request"]) != request: raise ValueError("Idempotency key reused with different settings")
                return old["id"],False
            db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?)",(rid,request["idempotency_key"],time.time(),time.time(),"queued",json.dumps(request),json.dumps(manifest),None))
        return rid,True

    def runs(self):
        with self.connect() as db: rows=db.execute("SELECT * FROM runs ORDER BY created DESC LIMIT 100").fetchall()
        return [self._run(r) for r in rows]

    def run(self,rid):
        with self.connect() as db: row=db.execute("SELECT * FROM runs WHERE id=?",(rid,)).fetchone()
        return self._run(row) if row else None

    def _run(self,row):
        value=dict(row)
        value["request"]=json.loads(value["request"])
        value["manifest"]=json.loads(value["manifest"])
        value.pop("key",None)
        return value

    def status(self,rid,status,error=None):
        with self.connect() as db: db.execute("UPDATE runs SET status=?,updated=?,error=? WHERE id=?",(status,time.time(),error,rid))
        self.event(rid,"stage",{"stage":status,"message":error})

    def event(self,rid,kind,data):
        with self.connect() as db:
            cur=db.execute("INSERT INTO events(run_id,time,kind,data) VALUES(?,?,?,?)",(rid,time.time(),kind,json.dumps(data)))
            return cur.lastrowid

    def events(self,rid,after=0):
        with self.connect() as db: rows=db.execute("SELECT * FROM events WHERE run_id=? AND id>? ORDER BY id LIMIT 1000",(rid,after)).fetchall()
        return [{**dict(r),"data":json.loads(r["data"])} for r in rows]

    def prediction(self,rid,pred):
        d=pred.model_dump() if hasattr(pred,"model_dump") else pred
        args=(rid,d["model_id"],d["case_id"],json.dumps(d))
        with self.connect() as db:
            db.execute("INSERT OR REPLACE INTO predictions VALUES(?,?,?,?)",args)
            db.execute("INSERT OR REPLACE INTO attempts VALUES(?,?,?,?,?)",(rid,d["model_id"],d["case_id"],d.get("attempt",1),json.dumps(d)))

    def predictions(self,rid,model=None):
        with self.connect() as db:
            rows=db.execute("SELECT data FROM predictions WHERE run_id=?"+(" AND model_id=?" if model else ""),(rid,model) if model else (rid,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def predictions_for_cases(self,rid,case_ids,model=None):
        if not case_ids:return []
        marks=",".join("?" for _ in case_ids)
        with self.connect() as db:
            rows=db.execute(f"SELECT data FROM predictions WHERE run_id=? AND case_id IN ({marks})"+
                (" AND model_id=?" if model else "")+" ORDER BY model_id,case_id",
                [rid,*case_ids,*([model] if model else [])]).fetchall()
        # The local evidence view needs labels/probabilities, not nested transport copies.
        return [{k:v for k,v in json.loads(r[0]).items() if k!='raw'} for r in rows]

    def prediction_summaries(self,rid,model=None):
        with self.connect() as db:
            rows=db.execute("SELECT model_id,case_id,json_extract(data,'$.status') AS status,"
                "json_extract(data,'$.selected') AS selected,json_extract(data,'$.request_ms') AS request_ms "
                "FROM predictions WHERE run_id=?"+(" AND model_id=?" if model else ""),
                (rid,model) if model else (rid,)).fetchall()
        return [dict(r) for r in rows]

    def setting(self,key,default=None):
        with self.connect() as db: row=db.execute("SELECT value FROM settings WHERE key=?",(key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set_setting(self,key,value):
        with self.connect() as db: db.execute("INSERT OR REPLACE INTO settings VALUES(?,?)",(key,json.dumps(value)))

    def judge_job(self,rid,jid,status,data):
        with self.connect() as db: db.execute("INSERT OR REPLACE INTO judge_jobs VALUES(?,?,?,?)",(rid,jid,status,json.dumps(data)))

    def judge_jobs(self,rid):
        with self.connect() as db: rows=db.execute("SELECT * FROM judge_jobs WHERE run_id=?",(rid,)).fetchall()
        return [{**dict(r),"data":json.loads(r["data"])} for r in rows]
