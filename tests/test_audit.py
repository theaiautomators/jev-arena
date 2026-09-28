from arena.audit import stratified_ids, disagreement_ids
from arena.fresh import fresh


def test_sample_is_independent_of_case_order_and_gold():
    cases = fresh()
    selected = stratified_ids(cases, 250)
    reversed_cases = [c.model_copy(update={'gold':c.question.labels[0]}) for c in reversed(cases)]
    assert selected == stratified_ids(reversed_cases, 250)
    assert len(selected) == len(set(selected)) == 250
    assert {c.family for c in cases if c.id in selected} == {c.family for c in cases}


def test_disagreement_sample_ignores_control_and_unsupported_results():
    a,b,c = fresh()[:3]
    rows = [
        {'case_id':a.id,'model_id':'one','status':'ok','selected':a.question.labels[0]},
        {'case_id':a.id,'model_id':'uniform','status':'ok','selected':a.question.labels[1]},
        {'case_id':b.id,'model_id':'one','status':'ok','selected':b.question.labels[0]},
        {'case_id':b.id,'model_id':'two','status':'invalid','selected':b.question.labels[1]},
        {'case_id':c.id,'model_id':'one','status':'ok','selected':c.question.labels[0]},
        {'case_id':c.id,'model_id':'two','status':'unsupported','selected':c.question.labels[1]},
    ]
    assert disagreement_ids([a,b,c],rows,set(),50) == [b.id]
    assert disagreement_ids([a,b,c],rows,{b.id},50) == []


def test_v2_routing_precedence_and_required_approval_are_explicit():
    cases = fresh()
    for case in cases:
        assert case.provenance['generator'] == 'formal-v2'
        if case.family == 'Support routing':
            assert 'route solely by the topic field' in case.state
            if case.question.kind == 'choice' and 'topic=payment' in case.state:
                assert case.gold == 'Billing'
        if case.family == 'Tool selection' and case.question.kind == 'noul':
            assert case.question.text == 'Does this task require approval that is not present?'
            assert (case.gold == 'yes') == ('needs write access' in case.state and 'Approval present=no' in case.state)


def test_reversal_changes_native_option_order_without_changing_meaning():
    import json
    from arena.contracts import Case, Question
    from arena.wire import native_question
    from scripts.run_video_evaluation import reversed_choice
    criteria={'bill':'Billing questions','tech':'Technical questions'}
    case=Case(id='order',cluster='order',pack='test',family='test',state='A payment issue.',gold='bill',
              question=Question(id='q',kind='choice',text='Choose a queue.',labels=list(criteria),criteria=criteria,rubric=json.dumps(criteria)))
    changed=reversed_choice(case)
    assert changed.gold==case.gold and changed.state==case.state
    assert changed.question.labels==['tech','bill']
    native=native_question(changed.question.model_dump())
    assert list(native['criteria'])==['tech','bill'] and native['criteria']==criteria
    assert list(json.loads(changed.question.rubric))==['tech','bill']
    assert list(case.question.criteria)==['bill','tech']
