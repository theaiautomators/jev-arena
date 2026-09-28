import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from arena import api, explorer
from arena.store import Store


@pytest.fixture
def evidence(tmp_path, monkeypatch):
    store = Store(tmp_path / 'test.sqlite3')
    store.create_run('fixture', {'idempotency_key': 'fixture-key', 'model_ids': ['a', 'b']}, {})
    monkeypatch.setattr(api.controller, 'store', store)
    monkeypatch.setattr(api, 'RUNS', tmp_path)
    folder = tmp_path / 'fixture'
    folder.mkdir()
    cases = [dict(id=f'c{i}', pack='Classification' if i < 4 else 'Other',
                  family='News' if i < 3 else 'Banking', state=f'Input needle-{i}',
                  question={'text': 'Pick a label', 'kind': 'choice', 'labels': ['yes', 'no', 'maybe']},
                  gold='yes', acceptable=['maybe'] if i == 0 else [],
                  label_status='teacher' if i == 5 else 'public') for i in range(6)]
    (folder / 'cases.jsonl').write_text('\n'.join(json.dumps(c) for c in cases), encoding='utf8')
    for m in ['a', 'b']:
        for i in range(6):
            if m == 'b' and i == 4:
                continue
            store.prediction('fixture', {'case_id': f'c{i}', 'model_id': m,
                'status': 'unsupported' if m == 'b' and i == 3 else 'invalid' if i == 1 else 'ok',
                'selected': 'maybe' if i == 0 else 'no' if i == 2 else 'yes',
                'request_ms': 20 + i, 'raw': {'huge_transport_copy': 'private'}})
    return store, folder, cases


def test_navigation_search_and_detail_are_scoped(evidence, monkeypatch):
    store, folder, cases = evidence
    monkeypatch.setattr(store, 'predictions', lambda *args: pytest.fail('Full prediction scan'))
    client = TestClient(api.app)
    d = client.get('/api/runs/fixture/cases?index_only=true&pack=Classification&family=News&offset=1&limit=1').json()
    assert d['total'] == 3 and d['cases'][0]['id'] == 'c1'
    assert 'state' not in d['cases'][0] and not d['predictions']
    assert sum(f['count'] for f in d['facets']) == 6
    d = client.get('/api/runs/fixture/cases?search=needle-4&limit=1').json()
    assert d['total'] == 1 and d['cases'][0]['id'] == 'c4'
    d = client.get('/api/runs/fixture/cases/c0?model=a').json()
    assert d['case'] == cases[0] and len(d['predictions']) == 1
    assert 'raw' not in d['predictions'][0]
    assert client.get('/api/runs/fixture/cases/missing').status_code == 404
    assert client.get('/api/runs/fixture/cases?offset=-1').status_code == 422
    assert client.get('/api/runs/fixture/cases?outcome=wrong').status_code == 422


def test_outcomes_distinguish_selected_answer_from_output_validity(evidence):
    client = TestClient(api.app)
    def ids(outcome, model='a'):
        return {c['id'] for c in client.get(f'/api/runs/fixture/cases?model={model}&outcome={outcome}').json()['cases']}
    assert ids('correct') == {'c0', 'c1', 'c3', 'c4', 'c5'}
    assert ids('wrong') == {'c2'}
    assert ids('failed') == {'c1'}
    assert ids('unsupported', 'b') == {'c3'}


def test_analysis_keeps_common_cohort_teachers_and_missing_distinct(evidence):
    result = TestClient(api.app).get('/api/runs/fixture/analysis').json()
    g = result['groups'][0]
    assert g['shared_n'] == 3 and g['reference_n'] == 5 and g['teacher_n'] == 1
    assert g['models']['a']['shared']['label_correct'] == 2
    assert g['models']['a']['shared']['strict_correct'] == 1
    assert g['models']['b']['supported']['unsupported'] == 1
    assert g['models']['b']['supported']['missing'] == 1
    assert g['models']['a']['teacher']['n'] == 1
    assert g['models']['a']['supported']['n'] == 5


def test_case_cache_invalidates_when_saved_file_changes(evidence):
    _, folder, cases = evidence
    assert len(explorer.saved_cases(folder)) == 6
    with (folder / 'cases.jsonl').open('a', encoding='utf8') as stream:
        stream.write('\n' + json.dumps({**cases[0], 'id': 'new'}))
    assert len(explorer.saved_cases(folder)) == 7


def test_published_findings_reconcile():
    root = Path(__file__).resolve().parents[1] / 'docs/evidence'
    data = json.loads((root / 'video-task-analysis.json').read_text())
    findings = json.loads((root / 'video-findings.json').read_text())
    news = next(g for g in data['groups'] if g['key'] == 'Classification::AG News')
    pair = findings['paired']['AG News']
    assert news['models']['laya']['shared']['label_correct'] == pair['both_correct'] + pair['a_only'] == 461
    assert news['models']['jev']['shared']['label_correct'] == pair['both_correct'] + pair['b_only'] == 441
    assert sum(pair[k] for k in ('both_correct', 'a_only', 'b_only', 'both_wrong')) == 500
    assert findings['relevance']['uniform']['positive']['correct'] == 0
    assert findings['relevance']['jev']['positive']['correct'] == 40
    assert findings['policy_weight']['n'] + findings['without_generated_policy']['jev']['n'] == 4635
