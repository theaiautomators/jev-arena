"""Summarize a completed run for independent review without copying case text."""
import argparse
import json
from collections import Counter,defaultdict
from pathlib import Path

from arena.config import write_json,ROOT
from arena.controller import Controller
from arena.scoring import statistical_clusters,summarize


def summarize_run(run_id):
    controller=Controller();run=controller.store.run(run_id)
    if not run or run['status']!='complete':
        raise ValueError('Review summaries require a completed run')
    cases=controller.cases(run_id);lookup={case.id:case for case in cases}
    results=controller.results(run_id,True);rows=controller.store.predictions(run_id)
    groups=statistical_clusters(cases);models=[]
    caution=json.loads((ROOT/'docs'/'reference-cautions.json').read_text(encoding='utf-8'))
    caution_ids=set(caution['case_ids'])
    unsupported={row['case_id'] for row in rows if row['status']=='unsupported'}
    sensitivity_cases=[case for case in cases if case.id not in caution_ids|unsupported]
    sensitivity={}
    for entrant in results['entrants']:
        selected=[row for row in rows if row['model_id']==entrant['id']]
        diagnostic=summarize(sensitivity_cases,selected,False)
        sensitivity[entrant['id']]={key:diagnostic[key] for key in ('correct','verified_count','accuracy','selected_label_correct','selected_label_accuracy')}
        verified=[row for row in selected if lookup[row['case_id']].label_status not in ('teacher','provisional') and row['status']!='unsupported']
        by_kind={}
        for kind in ('choice','noul','score'):
            cohort=[row for row in verified if lookup[row['case_id']].question.kind==kind]
            by_kind[kind]={'n':len(cohort),'correct':sum(row['status']=='ok' and row['selected'] in [lookup[row['case_id']].gold,*lookup[row['case_id']].acceptable] for row in cohort)}
        label_correct=sum(row['selected'] in [lookup[row['case_id']].gold,*lookup[row['case_id']].acceptable] for row in verified)
        episodes=defaultdict(list)
        for episode in results['episodes']:
            if episode['model_id']==entrant['id']:episodes[episode['task']+'/'+episode['mode']].append(episode)
        models.append({'id':entrant['id'],'name':entrant['name'],'metrics':entrant['metrics'],
                       'matched':entrant['matched'],'by_kind':by_kind,
                       'raw_label_diagnostic':{'n':len(verified),'correct':label_correct,
                                               'note':'Sensitivity check only: selected-label correctness ignores probability-contract validity; never substitutes for the frozen main metric.'},
                       'failures':dict(Counter(row.get('error') or row['status'] for row in selected if row['status'] not in ('ok','unsupported'))),
                       'unsupported':dict(Counter(row.get('error') or 'unspecified' for row in selected if row['status']=='unsupported')),
                       'episodes':{key:{'n':len(items),'success':sum(e['success'] for e in items),'violations':sum(e['violations'] for e in items),'deadline_misses':sum(e.get('deadline_misses') or 0 for e in items)} for key,items in episodes.items()}})
    disagreements=[]
    for job in results['judge_jobs']:
        data=job['data'];grade=data.get('grade')
        if job['status']!='complete' or not grade:continue
        case=lookup[data['item']['case_id']]
        if case.label_status in ('teacher','provisional'):continue
        reference_correct=data['item']['proposed_answer'] in [case.gold,*case.acceptable]
        if grade['verdict']=='ambiguous' or (grade['verdict'] in ('correct','acceptable'))!=reference_correct:
            disagreements.append({'case_id':case.id,'pack':case.pack,'models':data['models'],'reference_correct':reference_correct,'judge_verdict':grade['verdict'],'needs_human_review':grade['needs_human_review']})
    return {'run_id':run_id,'status':run['status'],'preset':run['request']['preset'],
            'created':run['created'],'case_count':len(cases),'scored_reference_cases':sum(c.label_status not in ('teacher','provisional') for c in cases),
            'statistical_clusters':len(set(groups.values())),
            'case_sha256':run['manifest']['case_sha256'],'runtime_fingerprint':run['manifest']['runtime_fingerprint'],
            'models':models,'comparisons':results['comparisons'],'judge_answer_reviews':sum(j['status']=='complete' for j in results['judge_jobs']),
            'judge_unique_case_count':len({j['data']['item']['case_id'] for j in results['judge_jobs'] if j['status']=='complete'}),
            'judge_reference_disagreements':disagreements,'publication_ready':False,
            'routing_ambiguity_sensitivity':{'basis':'Post-hoc exclusion on the shared supported reference cohort; never replaces primary results.',
                'excluded_case_ids':[case.id for case in cases if case.id in caution_ids],
                'models':sensitivity}}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('run_id');parser.add_argument('output',type=Path)
    arguments=parser.parse_args();write_json(arguments.output,summarize_run(arguments.run_id))
    print(f'Review summary saved: {arguments.output}')
