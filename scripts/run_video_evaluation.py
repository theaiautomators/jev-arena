"""Run the authorized video comparison and preserve resumable evidence."""
import argparse
import asyncio
import json
import time
from collections import Counter

from filelock import FileLock, Timeout
from arena import judge
from arena.adapters import Adapter
from arena.audit import stratified_ids
from arena.config import DATA, ROOT, RUNS, digest, write_json
from arena.contracts import RunRequest
from arena.controller import Controller
from arena.registry import REGISTRY
from arena.suites import suite

FOLDER = DATA / 'video-v2'
LAB_RESULT = ROOT / 'subprojects/decision-lab/.lab/runs/banking77-20260927-v1/results.json'


def progress(stage, **fields):
    value = {'stage':stage, 'updated':time.time(), **fields}
    write_json(FOLDER / 'progress.json', value)
    print(json.dumps(value), flush=True)


async def wait_for_gpu(wait_for_lab):
    while True:
        if wait_for_lab:
            try:
                ready = json.loads(LAB_RESULT.read_text(encoding='utf-8')).get('status') == 'complete'
            except (OSError, ValueError):
                ready = False
            if not ready:
                progress('waiting_for_support_lab')
                await asyncio.sleep(30)
                continue
        probe = FileLock(DATA / 'gpu.lock')
        try:
            probe.acquire(timeout=0)
        except Timeout:
            progress('waiting_for_gpu_lease')
            await asyncio.sleep(30)
        else:
            probe.release()
            return


def reversed_choice(case):
    altered = case.model_copy(deep=True)
    altered.question.labels.reverse()
    criteria = altered.question.criteria
    if isinstance(criteria, dict):
        altered.question.criteria = {label:criteria[label] for label in altered.question.labels}
        # Imported display rubrics repeat the criteria. Preserve meanings while
        # ensuring JSON-prompted and native competitors both see the new order.
        try:
            if json.loads(altered.question.rubric) == criteria:
                altered.question.rubric = json.dumps(altered.question.criteria, ensure_ascii=False)
        except (ValueError, TypeError):
            pass
    elif isinstance(criteria, list):
        altered.question.criteria = list(reversed(criteria))
    return altered


async def followups(ctl, rid):
    result = json.loads((RUNS / rid / 'results.json').read_text(encoding='utf-8'))
    eligible = [e for e in result['entrants'] if not e['hosted'] and e['id'] not in ('uniform','qwen','nli')]
    ranked = sorted(eligible, key=lambda e: (-(e['matched'].get('selected_label_accuracy') or 0), e['id']))
    models = ['jev'] + [e['id'] for e in ranked[:3]]
    rows = ctl.store.predictions(rid)
    unsupported = {p['case_id'] for p in rows if p['model_id'] in models and p['status'] == 'unsupported'}
    cases = [c for c in ctl.cases(rid) if c.id not in unsupported and c.label_status not in ('teacher','provisional') and c.question.kind == 'choice']
    ids = stratified_ids(cases, 200, seed=6091)
    lookup = {c.id:c for c in cases}
    frozen = {'models':models,'case_ids':ids,'selection':'Jev plus top three local candidates on all-entrant matched selected-label agreement; exact ties by entrant ID. Hash-stratified supported reference Choice cases, seed 6091. Follow-up results are descriptive and cannot change the primary scores.', 'main_run':rid}
    target = RUNS / rid / 'followups'
    existing = target / 'manifest.json'
    if existing.exists() and json.loads(existing.read_text(encoding='utf-8')) != frozen:
        raise RuntimeError('Follow-up selection changed; refusing mixed evidence')
    write_json(existing, frozen)
    baseline = {(p['model_id'],p['case_id']):p for p in rows}
    with FileLock(DATA / 'gpu.lock', timeout=0):
        for mid in models:
            location = target / 'workers' / mid
            journal = location / 'predictions.jsonl'
            location.mkdir(parents=True, exist_ok=True)
            done = []
            if journal.exists():
                done = [json.loads(line) for line in journal.read_text(encoding='utf-8').splitlines() if line]
            keys = {(r['case_id'],r['mode']) for r in done}
            if len(keys) == len(ids)*2:
                continue
            progress('followups', run_id=rid, model=mid, complete=len(done), total=len(ids)*2)
            adapter = Adapter(mid, location, asyncio.Event())
            try:
                await adapter.load()
                write_json(location / 'load.json', adapter.meta)
                for _ in range(10):
                    warm = await adapter.predict(lookup[ids[0]], cap=1)
                    if warm.status in ('timeout','transport_error'):
                        raise RuntimeError(f'Follow-up warmup failed: {mid}: {warm.error}')
                with journal.open('a', encoding='utf-8') as stream:
                    for cid in ids:
                        for mode in ('repeat','reversed_options'):
                            if (cid,mode) in keys:
                                continue
                            case = lookup[cid] if mode == 'repeat' else reversed_choice(lookup[cid])
                            pred = await adapter.predict(case, cap=1)
                            row = {'case_id':cid,'mode':mode,'prediction':pred.model_dump(),'input':case.candidate()}
                            stream.write(json.dumps(row, ensure_ascii=False)+'\n');stream.flush()
                            done.append(row)
                            if adapter.dead:
                                raise RuntimeError('Follow-up worker stopped')
            finally:
                cleanup = await adapter.unload()
                write_json(location / 'cleanup.json', cleanup)
                if cleanup.get('memory_within_baseline') is False:
                    raise RuntimeError('Follow-up GPU cleanup failed')
            summary = {'model':mid,'cases':len(ids),'cost_usd':adapter.cost,'modes':{}}
            for mode in ('repeat','reversed_options'):
                selected = [r for r in done if r['mode'] == mode]
                summary['modes'][mode] = {'n':len(selected),'valid':sum(r['prediction']['status']=='ok' for r in selected),
                    'strict_correct':sum(r['prediction']['status']=='ok' and r['prediction']['selected'] in [lookup[r['case_id']].gold,*lookup[r['case_id']].acceptable] for r in selected),
                    'selected_label_correct':sum(r['prediction']['selected'] in [lookup[r['case_id']].gold,*lookup[r['case_id']].acceptable] for r in selected),
                    'same_selected_as_main':sum(r['prediction']['selected'] is not None and r['prediction']['selected']==baseline[mid,r['case_id']]['selected'] for r in selected),
                    'statuses':dict(Counter(r['prediction']['status'] for r in selected))}
            write_json(location / 'summary.json', summary)
    progress('candidate_work_complete', run_id=rid, followup_models=models)


async def main(args):
    report = json.loads((DATA/'judge-controls'/judge.VERSION/'report.json').read_text(encoding='utf-8'))
    if not report['passed']:
        raise RuntimeError('Judge controls did not pass; full run was not started')
    ctl = Controller()
    request = RunRequest(preset='full', model_ids=list(REGISTRY), judge=True, judge_audit_cases=250,
                         judge_disagreement_cases=50, paid_cap_usd=5, seed=5090,
                         idempotency_key='video-all-roster-v2-20260927')
    freeze = {'request':request.model_dump(),'case_sha256':digest([c.model_dump() for c in suite('full')]),'protocol_sha256':digest((ROOT/'docs/VIDEO-EVALUATION-V2.md').read_bytes())}
    write_json(FOLDER/'launch-freeze.json',freeze)
    if args.resume:
        rid = args.resume
        if ctl.store.run(rid)['status'] != 'complete':
            await wait_for_gpu(args.wait_for_lab)
            await ctl.resume(rid)
    else:
        await wait_for_gpu(args.wait_for_lab)
        progress('native_clm_verification')
        from scripts.native_clm_parity import verify
        await verify()
        rid = await ctl.start(request)
        write_json(FOLDER/'run.json',{'run_id':rid})
    progress('running',run_id=rid)
    cursor = 0;last_print = 0
    while rid in ctl.tasks and not ctl.tasks[rid].done():
        for event in ctl.store.events(rid,cursor):
            cursor=event['id']
            if event['kind'] == 'prediction':
                if time.time()-last_print >= 30:
                    progress('evaluating',run_id=rid,**event['data']);last_print=time.time()
            elif event['kind'] in ('model','model_complete','judge_progress'):
                progress(event['kind'],run_id=rid,**event['data'])
        await asyncio.sleep(2)
    if rid in ctl.tasks:
        await ctl.tasks[rid]
    run = ctl.store.run(rid)
    if run['status'] != 'complete':
        raise RuntimeError(f"Run {rid}: {run['status']}: {run['error']}")
    await followups(ctl,rid)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--wait-for-lab',action='store_true')
    parser.add_argument('--resume')
    options=parser.parse_args()
    try:
        asyncio.run(main(options))
    except BaseException as error:
        progress('needs_attention',error=type(error).__name__+': '+str(error))
        raise
