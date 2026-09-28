import json
from arena import report

def test_public_report_omits_private_paths_errors_and_judge_quotes():
    secret='never-export-this-secret'
    result={k:[] for k in ('entrants','comparisons','limitations','episodes')}
    result.update(run_id='r',status='complete',kind='measured',preset='smoke',case_count=1,matched_count=1,publication_ready=False,performance={},judge_jobs=[{'status':'complete','data':{'rationale':secret}}])
    run={'id':'r','created':0,'status':'complete','error':secret,'request':{'preset':'smoke','model_ids':['uniform'],'judge':True},'manifest':{'version':'v1','entrants':[],'private_path':secret}}
    ready={'hardware':{'gpu':None,'platform':'Windows','disk_free_gb':100,'gpu_error':secret},'models':[],'suites':{},'judge':{'reason':secret,'version':'codex 0.157.1'},'setup':{'message':secret},'active_run':'r'}
    exported=report.public_report(result,run,ready)
    assert secret not in json.dumps(exported)
    assert exported['result']['judge_summary']['completed']==1


def test_export_keeps_blind_verdicts_without_prompts_or_evidence():
    secret='unpublished prompt or evidence'
    result={k:[] for k in ('entrants','comparisons','limitations','episodes')}
    result.update(run_id='r',status='complete',kind='measured',preset='smoke',case_count=1,matched_count=1,publication_ready=False,performance={},judge_jobs=[{'job_id':'j','status':'complete','data':{'models':['laya'],'item':{'case_id':'c','state':secret},'grade':{'verdict':'correct','needs_human_review':False,'rationale':secret,'evidence':secret}}}])
    run={'id':'r','created':0,'status':'complete','request':{'preset':'smoke','model_ids':['laya'],'judge':True},'manifest':{'entrants':[]}}
    ready={'hardware':{},'judge':{},'models':[],'suites':{}}
    exported=report.public_report(result,run,ready)
    assert secret not in json.dumps(exported)
    job=exported['result']['judge_jobs'][0]
    assert job['data']['models']==['laya']
    assert job['data']['grade']['verdict']=='correct'

def test_portable_report_escapes_untrusted_script_delimiters(tmp_path,monkeypatch):
    assets=tmp_path/'dist'/'assets';assets.mkdir(parents=True)
    (assets/'index-test.js').write_text('document.body.dataset.ready="yes";')
    (assets/'index-test.css').write_text('@font-face{font-family:Poppins;src:url(/assets/test.woff2) format("woff2"),url(/assets/test.woff) format("woff")}')
    (assets/'test.woff2').write_bytes(b'font-two')
    (assets/'test.woff').write_bytes(b'font-one')
    (tmp_path/'LICENSE').write_text('Arena MIT notice',encoding='utf-8')
    (tmp_path/'THIRD-PARTY-LICENSES.txt').write_text('Font license </script> retained',encoding='utf-8')
    monkeypatch.setattr(report,'ROOT',tmp_path)
    html=report.standalone({'label':'</script><script>alert(1)</script>'})
    assert '</script><script>alert' not in html
    assert '\\u003c/script\\u003e' in html
    assert '<script type="module">' in html
    assert 'Arena MIT notice' in html and 'Font license' in html
    assert 'id="arena-license-notices"' in html
    assert 'Font license </script>' not in html
    assert 'url(data:font/woff2;base64,' in html
    assert 'url(data:font/woff;base64,' in html
    assert 'url(/assets/' not in html


def test_export_uses_recorded_hardware_models_and_judge_version():
    result={key:[] for key in ('entrants','comparisons','limitations','episodes')}
    result.update(run_id='r',status='verifying',kind='measured',preset='smoke',case_count=1,matched_count=1,publication_ready=False,performance={},judge_jobs=[{'job_id':'j','status':'complete','data':{'models':['laya'],'item':{'case_id':'c'},'grade':{'verdict':'correct'},'metadata':{'cli':'recorded CLI','observed_model':None}}}])
    run={'id':'r','created':0,'status':'complete','request':{'preset':'smoke','model_ids':['laya'],'judge':True},'manifest':{'entrants':[{'id':'laya','revision':'recorded revision'}],'hardware':{'gpu':{'name':'recorded GPU','private_path':'must stay private'},'platform':'recorded OS'},'judge':{'requested_model':'gpt-6-astra'}}}
    current={'hardware':{'gpu':{'name':'different export GPU'}},'judge':{'version':'different export CLI'},'models':[{'id':'laya','revision':'different export revision'}]}
    exported=report.public_report(result,run,current)
    assert exported['result']['status']=='complete'
    assert exported['readiness']['hardware']['gpu']=={'name':'recorded GPU'}
    assert exported['readiness']['models'][0]['revision']=='recorded revision'
    assert exported['readiness']['judge']['version']=='recorded CLI'
    assert 'different export' not in json.dumps(exported)
    assert 'must stay private' not in json.dumps(exported)
