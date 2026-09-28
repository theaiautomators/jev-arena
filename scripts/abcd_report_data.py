"""Additional report-only checks and paired comparisons; no inference or gold edits."""
import itertools
import json
from collections import Counter
from pathlib import Path
from arena.config import ROOT, digest, write_json
from arena.contracts import Case
from scripts.analyze_abcd import FOLDER, RUN, CONDITIONS, rates, paired


def main():
    frozen = json.loads((FOLDER / 'test-freeze.json').read_text(encoding='utf-8'))
    summary = json.loads((ROOT / 'docs/evidence/abcd-v1-summary.json').read_text(encoding='utf-8'))
    for name, expected in frozen['fingerprint']['files'].items():
        assert digest((ROOT / name).read_bytes()) == expected, name
    cases = [Case.model_validate_json(x) for x in (FOLDER / 'test-cases.jsonl').read_text(encoding='utf-8').splitlines()]
    by_id = {c.id: c for c in cases}
    models = frozen['order']
    all_rows = {}; checks = {}; combined = {}; breakdown = {}
    caps = {'jev': 32000, 'decider': 32768, 'winnow': 65536, 'nimble': 8192, 'qwen': 32768-128}
    for model in models:
        path = RUN / 'workers' / model / 'predictions.jsonl'
        assert digest(path.read_bytes()) == summary['verification']['journal_sha256'][model]
        rows = [json.loads(x)['prediction'] for x in path.read_text(encoding='utf-8').splitlines()]
        ps = {p['case_id']: p for p in rows}; all_rows[model] = ps
        assert len(ps) == len(rows) == 2544
        for p in rows:
            tokens = p['input_tokens']
            if tokens is None:
                assert p['status'] == 'transport_error' and p['selected'] is None
            elif p['status'] == 'unsupported':
                assert tokens > caps[model], (model, p['case_id'])
            else:
                assert 0 < tokens <= caps[model], (model, p['case_id'])
        checks[model] = {'statuses': dict(Counter(p['status'] for p in rows)),
                         'max_reported_input_tokens': max(p['input_tokens'] or 0 for p in rows),
                         'capacity_checks_passed': True,
                         'warmup_records': len(list((RUN / 'workers' / model).glob('warmup-*.json')))}
        combined[model] = {}; breakdown[model] = {}
        for cond in CONDITIONS:
            natural = [c for c in cases if c.pack == 'ABCD next action' and c.provenance['condition'] == cond]
            actions = {(c.cluster, c.provenance['checkpoint_index']): c for c in natural if c.family == 'action'}
            observations = []; route_groups = {}
            for c in sorted((c for c in natural if c.family == 'route'), key=lambda c: (c.cluster, c.provenance['checkpoint_index'])):
                required = [c]
                if c.gold == 'take_action': required.append(actions[c.cluster, c.provenance['checkpoint_index']])
                supported = all(ps[x.id]['status'] != 'unsupported' for x in required)
                label = all(ps[x.id]['selected'] == x.gold for x in required)
                strict = label and all(ps[x.id]['status'] == 'ok' for x in required)
                o = {'case_id': c.id, 'cluster': c.cluster, 'supported': supported,
                     'strict': strict, 'label': label, 'status': 'ok' if supported else 'unsupported'}
                observations.append(o)
                route_groups.setdefault(c.gold, []).append(o)
            result = rates(observations)
            for key in ('planned', 'supported', 'unsupported', 'strict_correct', 'label_correct'):
                assert result[key] == summary['models'][model]['combined'][cond][key]
            combined[model][cond] = observations
            breakdown[model][cond] = {k: rates(v) for k, v in route_groups.items()}
            breakdown[model][cond]['nonterminal'] = rates([o for o in observations if by_id[o['case_id']].gold != 'end_conversation'])
    comparisons = {cond: {a+' -> '+b: paired(combined[a][cond], combined[b][cond])
                          for a,b in itertools.combinations(models, 2)} for cond in CONDITIONS}
    supports = Counter(c.gold for c in cases if c.pack == 'ABCD next action' and c.family == 'action' and c.provenance['condition'] == 'full_handbook')
    result = {'id': 'abcd-test-v1', 'frozen_source_and_journal_hashes_unchanged': True,
              'independent_combined_reconstruction_passed': True, 'capacity': checks,
              'combined_pairwise': comparisons, 'combined_by_true_route': breakdown,
              'action_support': dict(sorted(supports.items())),
              'constant_baselines': {'balanced_route': 1/3, 'always_end_combined': 1/3,
                                     'largest_action_share': max(supports.values())/300,
                                     'note': 'Descriptive constant-label baselines on the selected test distribution, not trained predictors.'},
              'limitations': ['Terminal checkpoint is synthesized after the observed dialogue; separately show nonterminal performance.',
                              'Pairwise intervals resample the same 300 conversation clusters, 10,000 times; unadjusted descriptive comparisons.']}
    write_json(ROOT / 'docs/evidence/abcd-v1-supplement.json', result)
    write_json(RUN / 'report-checks.json', result)
    print(json.dumps({'verified': True, 'records': 12720, 'capacity': checks}))


if __name__ == '__main__': main()
