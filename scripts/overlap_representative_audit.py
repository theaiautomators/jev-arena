"""Prefetch the frozen representative audit while candidates use the GPU.

Does not change the candidate runner, scoring, audit selection or judge rubric.
Only complete, verified grades are cached. The main judge owns all remaining
work. The finalizer refreshes model attribution using the finished predictions.
"""
import argparse
import asyncio
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

from filelock import FileLock
from arena import judge
from arena.config import DATA, ROOT, RUNS, digest, write_json
from arena.contracts import Case
from arena.store import Store

CANDIDATE_STAGES = {'loading', 'warming', 'evaluating', 'performance', 'episodes', 'unloading', 'preflight'}


def select_jobs(cases, rows, audit_ids, model_ids):
    lookup = {c.id: c for c in cases}
    groups = defaultdict(list)
    for p in rows:
        if p['model_id'] not in model_ids or p['case_id'] not in audit_ids:
            continue
        c = lookup[p['case_id']]
        if p['status'] in ('ok', 'invalid') and p['selected'] in c.question.labels:
            groups[c.id, p['selected']].append(p['model_id'])
    jobs = []
    for (cid, answer), models in groups.items():
        c = lookup[cid]
        item = {'case_id':cid, 'question_id':c.question.id, 'state':c.state,
                'question':c.question.text, 'rubric':c.question.rubric,
                'allowed_answers':c.question.labels, 'proposed_answer':answer}
        jobs.append({'job_id':digest([cid, answer, judge.VERSION])[:20],
                     'item':item, 'models':sorted(models),
                     'role':'semantic_grade' if c.label_status in ('provisional','audited') else 'reference_audit'})
    return sorted(jobs, key=lambda j: j['job_id'])


def cache_batch(store, rid, batch, result):
    """Atomically refuse new imports after the main runner starts judging."""
    grades = {g['case_id']:g for g in result['grades']}
    with store.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        status = db.execute('SELECT status FROM runs WHERE id=?',(rid,)).fetchone()[0]
        if status not in CANDIDATE_STAGES:
            return 0
        imported = 0
        for job in batch:
            existing = db.execute('SELECT status FROM judge_jobs WHERE run_id=? AND job_id=?',
                                  (rid,job['job_id'])).fetchone()
            if existing and existing[0] == 'complete':
                continue
            data = {'models':job['models'], 'models_at_grade_time':job['models'],
                    'item':job['item'], 'grade':grades[job['item']['case_id']],
                    'metadata':result['metadata'], 'role':job['role'],
                    'prefetched_representative':True}
            db.execute('INSERT OR REPLACE INTO judge_jobs VALUES(?,?,?,?)',
                       (rid,job['job_id'],'complete',json.dumps(data)))
            imported += 1
        return imported


def refresh_attribution(store, rid, folder):
    """Join cached case/answer grades to final model outputs; never regrade."""
    groups = defaultdict(list)
    for p in store.predictions(rid):
        if p['status'] in ('ok','invalid'):
            groups[p['case_id'],p['selected']].append(p['model_id'])
    changes = []
    for job in store.judge_jobs(rid):
        data = job['data']
        if job['status'] != 'complete' or not data.get('prefetched_representative'):
            continue
        item = data['item']
        models = sorted(groups[item['case_id'],item['proposed_answer']])
        if sorted(data['models']) != models:
            changes.append({'job_id':job['job_id'],'before':data['models'],'after':models})
            data['models'] = models
            data['attribution_refreshed_from_predictions'] = True
            store.judge_job(rid,job['job_id'],'complete',data)
    if changes:
        write_json(folder/'attribution-refresh.json',{'updated':time.time(),'changes':changes})
    return len(changes)


async def run(rid):
    store = Store()
    folder = RUNS/rid/'overlap-audit'
    folder.mkdir(parents=True, exist_ok=True)
    def progress(stage, **fields):
        value = {'stage':stage,'updated':time.time(),'run_id':rid,**fields}
        write_json(folder/'progress.json',value)
        print(json.dumps(value),flush=True)
    with FileLock(folder/'worker.lock',timeout=0):
        run_data = store.run(rid)
        manifest = run_data['manifest']
        if manifest['judge']['rubric'] != judge.VERSION:
            raise RuntimeError('Judge rubric differs from the frozen run')
        if not json.loads((DATA/'judge-controls'/judge.VERSION/'report.json').read_text(encoding='utf-8'))['passed']:
            raise RuntimeError('Judge controls must pass before prefetch')
        cases = [Case(**json.loads(line)) for line in (RUNS/rid/'cases.jsonl').read_text(encoding='utf-8').splitlines()]
        plan_file = folder/'plan.json'
        if plan_file.exists():
            plan = json.loads(plan_file.read_text(encoding='utf-8'))
        else:
            rows = store.predictions(rid)
            counts = Counter(p['model_id'] for p in rows)
            models = sorted(m for m,n in counts.items() if n == len(cases))
            ids = set(manifest['judge']['audit_ids'])
            plan = {'run_id':rid,'created':time.time(),'representative_ids':sorted(ids),
                    'snapshot_models':models,'jobs':select_jobs(cases,rows,ids,models),
                    'scope':'Frozen representative audit only. Snapshot of completed models, deduplicated case/answer pairs. One remote Codex CLI batch at a time, maximum eight answers. No GPU use; no extra audit questions. Main runner grades new answers and the later disagreement sample.',
                    'script_sha256':digest(Path(__file__).read_bytes()),'rubric':judge.VERSION}
            write_json(plan_file,plan)
            (folder/'script-snapshot.py').write_bytes(Path(__file__).read_bytes())
        done = {j['job_id'] for j in store.judge_jobs(rid) if j['status']=='complete'}
        pending = [j for j in plan['jobs'] if j['job_id'] not in done]
        total = len(plan['jobs'])
        progress('prefetching',complete=total-len(pending),total=total)
        try:
            while pending:
                if store.run(rid)['status'] not in CANDIDATE_STAGES:
                    break
                batch=[]; seen=set()
                for job in pending:
                    if job['item']['case_id'] not in seen:
                        batch.append(job);seen.add(job['item']['case_id'])
                    if len(batch)==8:break
                items = [j['item'] for j in batch]
                batchid = 'overlap-'+digest(items)[:16]
                result = None
                for attempt in (1,2):
                    target = RUNS/rid/'judge'/batchid/f'attempt-{attempt}'
                    if (target/'answer.json').exists() and (target/'metadata.json').exists():
                        # Completed imports are already skipped above. Never
                        # silently overwrite evidence after an interrupted import.
                        attempt = max([int(p.name.split('-')[-1]) for p in target.parent.glob('attempt-*')]+[attempt])+1
                        target = target.parent/f'attempt-{attempt}'
                    try:
                        result = await judge.grade(items,target)
                        break
                    except judge.JudgePaused:raise
                    except Exception:
                        if attempt>=2:raise
                imported = cache_batch(store,rid,batch,result)
                if imported == 0:
                    break
                selected = {j['job_id'] for j in batch}
                pending = [j for j in pending if j['job_id'] not in selected]
                progress('prefetching',complete=total-len(pending),total=total)
            refresh_attribution(store,rid,folder)
            progress('snapshot_complete' if not pending else 'yielded_to_main',complete=total-len(pending),total=total)
        except Exception as error:
            progress('needs_attention',error=type(error).__name__+': '+str(error),complete=total-len(pending),total=total)
            raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run_id');p.add_argument('--refresh-attribution',action='store_true');a=p.parse_args()
    if a.refresh_attribution:
        print(refresh_attribution(Store(),a.run_id,RUNS/a.run_id/'overlap-audit'))
    else:
        asyncio.run(run(a.run_id))
