"""Reproduce descriptive video findings from frozen records; no model calls."""
import argparse
from collections import Counter
import json
from pathlib import Path

from arena.config import ROOT, RUNS
from arena.explorer import matches, saved_cases, summarize


def analyze(rid):
    folder = RUNS / rid
    cases = saved_cases(folder)
    run = json.loads((folder / 'run.json').read_text(encoding='utf-8'))
    result = json.loads((folder / 'results.json').read_text(encoding='utf-8'))
    models = run['request']['model_ids']
    with (folder / 'predictions.jsonl').open(encoding='utf-8') as stream:
        predictions = [{k: p.get(k) for k in ('case_id', 'model_id', 'status', 'selected', 'request_ms')}
                       for line in stream if line.strip() for p in [json.loads(line)]]
    rows = {m: {p['case_id']: p for p in predictions if p['model_id'] == m} for m in models}
    assert len(predictions) == len(cases) * len(models)
    assert all(len(v) == len(cases) for v in rows.values())
    data = {'run_id': rid, **summarize(cases, predictions, models)}
    all_group = data['groups'][0]
    for e in result['entrants']:
        for scope, saved in [('shared', e['matched']), ('supported', e['metrics'])]:
            actual = all_group['models'][e['id']][scope]
            assert (actual['n'], actual['label_correct'], actual['strict_correct']) == (
                saved['verified_count'], saved['selected_label_correct'], saved['correct'])
    common = [c for c in cases if c['label_status'] not in ('teacher', 'provisional') and
              all(rows[m][c['id']]['status'] != 'unsupported' for m in models)]
    def score(cohort, m):
        correct = sum(matches(c, rows[m][c['id']]) for c in cohort)
        return {'n': len(cohort), 'correct': correct, 'accuracy': correct / len(cohort)}
    policy = [c for c in common if c['pack'] in ('Arena Fresh', 'Robustness')]
    remaining = [c for c in common if c not in policy]
    sensitivity = {m: score(remaining, m) for m in models}
    paired = {}
    for family, a, b in [('AG News', 'laya', 'jev'), ('XNLI', 'decider', 'jev')]:
        cohort = [c for c in common if c['family'] == family]
        counts = Counter((matches(c, rows[a][c['id']]), matches(c, rows[b][c['id']])) for c in cohort)
        examples = [c['id'] for c in cohort if matches(c, rows[a][c['id']]) and not matches(c, rows[b][c['id']])]
        paired[family] = {'a': a, 'b': b, 'n': len(cohort), 'both_correct': counts[True, True],
            'a_only': counts[True, False], 'b_only': counts[False, True], 'both_wrong': counts[False, False],
            'a_only_example_ids': examples[:8], 'a_only_disagreements': [
                {'gold': g, 'b_selected': selected, 'n': n} for (g, selected), n in Counter(
                    (c['gold'], rows[b][c['id']]['selected']) for c in cohort if c['id'] in examples).items()]}
    scifact = [c for c in common if c['family'] == 'SciFact']
    relevance = {}
    for m in models:
        confusion = Counter((c['gold'], rows[m][c['id']]['selected']) for c in scifact)
        positives = [c for c in scifact if c['gold'] == 'yes']
        predicted_positive = sum(p == 'yes' for _, p in ((c['gold'], rows[m][c['id']]['selected']) for c in scifact))
        tp = sum(matches(c, rows[m][c['id']]) for c in positives)
        relevance[m] = {'accuracy': score(scifact, m), 'gold_counts': dict(Counter(c['gold'] for c in scifact)),
            'confusion': [{'gold': g, 'selected': p, 'n': n} for (g, p), n in confusion.items()],
            'positive_labels': ['yes'], 'positive': score(positives, m),
            'positive_precision': tp / predicted_positive if predicted_positive else None}
    output = ROOT / 'docs/evidence'
    (output / 'video-task-analysis.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    findings = {'run_id': rid, 'verification': 'All 13 aggregate counts match frozen results.json.',
        'scope': 'Post-hoc descriptive slices, not new primary scores or independent significance claims.',
        'policy_weight': {'n': len(policy), 'shared_n': len(common), 'fraction': len(policy) / len(common)},
        'without_generated_policy': sensitivity, 'paired': paired, 'relevance': relevance}
    source = ROOT / '.arena/datasets/raw/fancyzhx--ag_news/data/test-00000-of-00001.parquet'
    reference_inspection = []
    if source.exists():
        import pyarrow.parquet as pq
        table = pq.read_table(source)
        for index in (450, 614, 1617):
            case = next(c for c in cases if c['id'] == f'classification-ag news-{index}')
            original = table.slice(index, 1).to_pylist()[0]
            assert original['text'] == case['state'] and original['label'] == 0 and case['gold'] == 'World'
            reference_inspection.append({'case_id': case['id'], 'source_index': index,
                'source_revision': case['provenance']['revision'], 'text_and_label_match_source': True,
                'reference': case['gold'], 'jev': rows['jev'][case['id']]['selected'],
                'laya': rows['laya'][case['id']]['selected']})
    findings['reference_inspection'] = reference_inspection
    (output / 'video-findings.json').write_text(json.dumps(findings, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in findings.items() if k != 'relevance'}, indent=2))
    print('SciFact', json.dumps({m: relevance[m] for m in ('uniform', 'jev', 'winnow', 'decider', 'laya')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id', nargs='?', default='20260927-205440-6350b9')
    analyze(parser.parse_args().run_id)
