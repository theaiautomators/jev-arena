import pytest
from arena.wire import native_question,normalize_answer,semif_row,capability_error


def test_imported_native_criteria_are_not_duplicated_in_instructions():
    q={'kind':'choice','text':'Route this ticket.','labels':['a','b'],
       'rubric':'{"a":"Billing","b":"Technical"}',
       'criteria':{'a':'Billing','b':'Technical'}}
    assert native_question(q)=={'type':'choice','instructions':'Route this ticket.','criteria':q['criteria']}
    row=semif_row({'case_id':'c','state':'Duplicate charge.','question':q})
    assert row['question']=='Route this ticket.'
    assert row['options']==[{'id':'a','description':'a: Billing'},{'id':'b','description':'b: Technical'}]


def test_semif_noul_preserves_author_true_false_order_and_descriptions():
    q={'kind':'noul','text':'Is it urgent?','labels':['no','yes'],
       'criteria':{'true':'Needs action now','false':'Can wait'}}
    row=semif_row({'case_id':'c','state':'x','question':q})
    assert row['options']==[{'id':'true','description':'true: Needs action now'},
                            {'id':'false','description':'false: Can wait'}]


def test_absent_native_criteria_stay_absent_without_empty_json_rubric():
    q={'kind':'noul','text':'Is it urgent?','labels':['no','yes'],'rubric':'{}','criteria':None}
    assert native_question(q)=={'type':'noul','instructions':'Is it urgent?'}
    row=semif_row({'case_id':'c','state':'x','question':q})
    assert row['options'][0]['description']=='true: The proposition is true.'


def test_native_choice_survives_rounded_probability_tie():
    q={'kind':'choice','labels':['a','b']}
    assert normalize_answer({'choice':'b','probabilities':{'a':.5,'b':.5}},q)['selected']=='b'
    with pytest.raises(ValueError,match='boolean'):
        normalize_answer({'noul':True},{'kind':'noul','labels':['no','yes']})


def test_only_known_native_context_limits_are_capability_exclusions():
    assert capability_error(ValueError('Row x: 8200 input tokens exceed limit 8192; no truncation allowed'))
    assert capability_error(ValueError('Longest prompt has 8200 tokens; limit is 8192. Nothing was truncated.'))
    assert not capability_error(RuntimeError('CUDA out of memory'))
