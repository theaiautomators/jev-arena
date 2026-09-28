from arena.config import digest
from arena.fresh import smoke
from arena.store import Store
from arena import judge
from scripts.overlap_representative_audit import select_jobs,cache_batch,refresh_attribution


def setup_store(tmp_path):
    store=Store(tmp_path/'test.db')
    store.create_run('run',{'idempotency_key':'overlap-test'}, {})
    store.status('run','evaluating')
    return store


def sample():
    case=smoke()[0]
    answer=case.question.labels[0]
    row={'case_id':case.id,'model_id':'a','selected':answer,'status':'invalid'}
    job=select_jobs([case],[row],{case.id},{'a'})[0]
    result={'grades':[{'case_id':case.id,'question_id':case.question.id,'verdict':'correct'}], 'metadata':{'rubric_version':judge.VERSION}}
    return case,row,job,result


def test_only_frozen_questions_and_eligible_selected_labels_are_prefetched():
    case,row,job,_=sample()
    other=smoke()[1]
    rows=[row,{**row,'model_id':'b'}, {**row,'model_id':'c','selected':'not-an-allowed-label'},
          {**row,'case_id':other.id}, {**row,'model_id':'d','status':'unsupported'}]
    jobs=select_jobs([case,other],rows,{case.id},{'a','c','d'})
    assert jobs==[job]
    assert job['job_id']==digest([case.id,row['selected'],judge.VERSION])[:20]
    assert not {'models','gold','probabilities','request_ms'} & job['item'].keys()


def test_judging_transition_rejects_prefetch_import(tmp_path):
    store=setup_store(tmp_path)
    _,_,job,result=sample()
    store.status('run','judging')
    assert cache_batch(store,'run',[job],result)==0
    assert store.judge_jobs('run')==[]


def test_completed_judgments_are_never_overwritten(tmp_path):
    store=setup_store(tmp_path)
    _,_,job,result=sample()
    assert cache_batch(store,'run',[job],result)==1
    result['grades'][0]['verdict']='incorrect'
    assert cache_batch(store,'run',[job],result)==0
    assert store.judge_jobs('run')[0]['data']['grade']['verdict']=='correct'


def test_later_models_inherit_only_the_matching_answer_grade(tmp_path):
    from arena.contracts import Prediction
    store=setup_store(tmp_path)
    case,row,job,result=sample()
    cache_batch(store,'run',[job],result)
    for model,answer,status in [('a',row['selected'],'invalid'),('b',row['selected'],'ok'),
                                ('c',case.question.labels[1],'ok'),('d',row['selected'],'unsupported')]:
        store.prediction('run',Prediction(case_id=case.id,model_id=model,status=status,selected=answer))
    assert refresh_attribution(store,'run',tmp_path)==1
    data=store.judge_jobs('run')[0]['data']
    assert data['models']==['a','b']
    assert data['models_at_grade_time']==['a']
    assert data['grade']==result['grades'][0]
