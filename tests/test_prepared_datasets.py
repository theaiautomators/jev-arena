import pytest
from collections import Counter,defaultdict
from arena.config import DATASETS,SOURCES
from arena.suites import suite
from arena.wire import native_question

pytestmark=pytest.mark.skipif(not (DATASETS/'multilingual-cases.jsonl').exists() or not (SOURCES/'jevbench').exists(),reason='Public datasets are intentionally not downloaded in CPU CI')

def test_prepared_full_suite_alignment_and_denominators():
    cases=suite('full')
    assert len(cases)==7671 and len({c.id for c in cases})==7671
    classification=Counter(c.family for c in cases if c.pack=='Classification')
    assert len(classification)==3 and set(classification.values())=={500}
    translations=defaultdict(list)
    for c in cases:
        if c.pack=='Multilingual':translations[c.cluster].append(c)
    assert len(translations)==200
    for aligned in translations.values():
        assert {c.language for c in aligned}=={'en','es','de','hi','ar'}
        assert len({c.gold for c in aligned})==1
    retrieval=Counter(c.cluster for c in cases if c.family=='SciFact')
    assert len(retrieval)==50 and set(retrieval.values())=={10}


def test_every_imported_native_question_matches_the_source_payload():
    imported=[c for c in suite('full') if c.provenance.get('native_question')]
    assert len(imported)==2231
    assert all(native_question(c.question.model_dump())==c.provenance['native_question'] for c in imported)
