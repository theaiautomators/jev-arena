"""Independent count checks and compact evidence for the video comparison."""
import argparse
import json
from collections import Counter, defaultdict

from arena.config import ROOT, RUNS, digest, write_json
from scripts.public_evidence import public_evidence


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def analyze(rid):
    folder=RUNS/rid
    run=read(folder/'run.json');manifest=read(folder/'manifest.json');result=read(folder/'results.json')
    cases=[json.loads(line) for line in (folder/'cases.jsonl').read_text(encoding='utf-8').splitlines()]
    predictions=[json.loads(line) for line in (folder/'predictions.jsonl').read_text(encoding='utf-8').splitlines()]
    assert run['status']==result['status']=='complete'
    assert digest(cases)==manifest['case_sha256']
    assert len(cases)==7671
    lookup={c['id']:c for c in cases}
    keys={(p['model_id'],p['case_id']) for p in predictions}
    models=run['request']['model_ids']
    assert len(keys)==len(predictions)==len(cases)*len(models)
    assert set(models)=={p['model_id'] for p in predictions}
    overlap=folder/'overlap-audit'
    if (overlap/'plan.json').exists():
        # A cached case/answer grade also applies to later models choosing that
        # answer. Refresh attribution only; preserve every grade and old export.
        from arena.store import Store
        from scripts.overlap_representative_audit import refresh_attribution
        store=Store()
        before={j['job_id']:j['data'].get('grade') for j in store.judge_jobs(rid)}
        refresh_attribution(store,rid,overlap)
        jobs=store.judge_jobs(rid)
        assert before=={j['job_id']:j['data'].get('grade') for j in jobs}
        if result['judge_jobs']!=jobs:
            prior=overlap/'results-before-attribution-refresh.json'
            if not prior.exists():write_json(prior,result)
            result['judge_jobs']=jobs
            write_json(folder/'results.json',result)
            exported=folder/'judge-jobs.jsonl'
            prior_lines=overlap/'judge-jobs-before-attribution-refresh.jsonl'
            if exported.exists() and not prior_lines.exists():prior_lines.write_bytes(exported.read_bytes())
            exported.write_text('\n'.join(json.dumps(j,ensure_ascii=False) for j in jobs)+'\n',encoding='utf-8')
        matching=defaultdict(set)
        for p in predictions:
            if p['status'] in ('ok','invalid'):
                matching[p['case_id'],p['selected']].add(p['model_id'])
        for j in jobs:
            item=j['data']['item']
            assert set(j['data']['models'])==matching[item['case_id'],item['proposed_answer']]
    by_model=defaultdict(list)
    for p in predictions:
        c=lookup[p['case_id']]
        assert p['input_hash']==digest({'case_id':c['id'],'state':c['state'],'question':c['question']})
        by_model[p['model_id']].append(p)
    excluded={p['case_id'] for p in predictions if p['status']=='unsupported'}
    reference={c['id'] for c in cases if c['label_status'] not in ('teacher','provisional')}
    shared=reference-excluded
    def counts(rows,ids):
        cohort=[p for p in rows if p['case_id'] in ids and p['status']!='unsupported']
        correct=lambda p:p['selected'] in [lookup[p['case_id']]['gold'],*lookup[p['case_id']]['acceptable']]
        strict=sum(p['status']=='ok' and correct(p) for p in cohort)
        labels=sum(correct(p) for p in cohort)
        return {'n':len(cohort),'strict_correct':strict,'label_correct':labels,'strict_accuracy':strict/len(cohort) if cohort else None,'label_accuracy':labels/len(cohort) if cohort else None}
    independent={}
    for mid,rows in by_model.items():
        assert len(rows)==7671
        independent[mid]={'reference':counts(rows,reference),'shared_reference':counts(rows,shared),
                          'status_counts':dict(Counter(p['status'] for p in rows)),
                          'languages':{lang:counts(rows,{c['id'] for c in cases if c['id'] in reference and c['language']==lang}) for lang in sorted({c['language'] for c in cases})},
                          'packs':{pack:counts(rows,{c['id'] for c in cases if c['id'] in reference and c['pack']==pack}) for pack in sorted({c['pack'] for c in cases if c['id'] in reference})}}
        original=next(e for e in result['entrants'] if e['id']==mid)
        for scope,key in [('reference','metrics'),('shared_reference','matched')]:
            actual=independent[mid][scope];saved=original[key]
            assert (actual['n'],actual['strict_correct'],actual['label_correct'])==(saved['verified_count'],saved['correct'],saved['selected_label_correct']),mid
        assert len(result['performance'][mid]['blocks'])==3
        episodes=[e for e in result['episodes'] if e['model_id']==mid]
        assert len(episodes)==80
        assert all(sum(len(e['trace']) for e in episodes if e['task']==task and e['mode']==mode)>0 for task in ('tickets','warehouse') for mode in ('untimed_quality','deadline_500ms'))
        cleanup=read(folder/'workers'/mid/'cleanup.json')
        if mid not in ('jev','uniform'):
            assert cleanup['container_stopped'] and cleanup['memory_within_baseline']
            for cycle in (2,3):
                proof=read(folder/'workers'/mid/f'cycle-{cycle}-cleanup.json')
                assert proof['container_stopped'] and proof['memory_within_baseline']
    selection=read(folder/'audit-selection.json')
    selected=set(selection['representative_ids'])|set(selection['disagreement_ids'])
    assert len(selection['representative_ids'])==250 and len(selection['disagreement_ids'])<=50
    assert set(selection['representative_ids'])==set(manifest['judge']['audit_ids'])
    judges=result['judge_jobs']
    assert all(j['status']=='complete' for j in judges)
    judged={j['data']['item']['case_id'] for j in judges}
    # Cases can lack an answer to review; make any such gap explicit.
    audit={'representative_questions':len(selection['representative_ids']),'disagreement_questions':len(selection['disagreement_ids']),
           'judged_questions':len(judged),'answer_reviews':len(judges),'selected_without_valid_label':sorted(selected-judged)}
    for name,ids in [('representative',set(selection['representative_ids'])),('disagreement',set(selection['disagreement_ids']))]:
        subset=[j for j in judges if j['data']['item']['case_id'] in ids]
        audit[name]={'questions':len({j['data']['item']['case_id'] for j in subset}), 'reviews':len(subset),'verdicts':dict(Counter(j['data']['grade']['verdict'] for j in subset))}
    usage=Counter();calls=0
    for path in (folder/'judge').glob('*/attempt-*/events.jsonl'):
        for line in path.read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('usage'):
                usage.update({k:v for k,v in event['usage'].items() if isinstance(v,(int,float))});calls+=1
    audit['cli_calls_with_usage']=calls;audit['token_usage']=dict(usage)
    audit['standard_credit_equivalent']=((usage['input_tokens']-usage['cached_input_tokens'])*250+usage['cached_input_tokens']*25+usage['output_tokens']*1250)/1e6
    summary=public_evidence(rid)
    summary['independent_counts']=independent;summary['expanded_audit']=audit
    summary['suite_version']=manifest['version'];summary['fixture_version']=manifest.get('fixture_version')
    summary['jev_ledger']=read(folder/'workers'/'jev'/'cost-ledger.json')
    summary['followups']={p.parent.name:read(p) for p in (folder/'followups'/'workers').glob('*/summary.json')}
    summary['verification']={'record_count':len(predictions),'unique_record_count':len(keys),'case_and_candidate_hashes_match':True,
                             'all_model_counts_match':True,'timing_blocks':len(models)*3,'workflow_episodes':len(result['episodes']),'all_local_cleanup_cycles_passed':True}
    path=ROOT/'docs'/'evidence'/'full-v2-summary.json'
    write_json(path,summary)
    write_json(folder/'independent-verification.json',summary['verification'])
    print(json.dumps({'run_id':rid,'verified':summary['verification'],'audit':audit,'models':{m:v['shared_reference'] for m,v in independent.items()}},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run_id');a=p.parse_args();analyze(a.run_id)
