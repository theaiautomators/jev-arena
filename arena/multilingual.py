"""Use the official pinned MASSIVE parquet conversion, avoiding a 52-locale archive."""
import json
from arena.importers import LANGS,parquet,stratified,save,provenance,rag,file
from arena.contracts import Case,Question
from arena.config import DATASETS,digest,write_json
from huggingface_hub import hf_hub_download
import pyarrow.parquet as pq
import ast

def run():
    cases=[];repo='facebook/xnli';rows=parquet(repo,'all_languages/test-00000-of-00001.parquet');labels=['entailment','neutral','contradiction']
    for i in stratified(rows,100):
        r=rows[i];hyp=dict(zip(r['hypothesis']['language'],r['hypothesis']['translation']))
        for lang in LANGS:
            cases.append(Case(id=f'xnli-{i}-{lang}',cluster=f'xnli-{i}',pack='Multilingual',family='XNLI',language=lang,state=f"Premise: {r['premise'][lang]}\nHypothesis: {hyp[lang]}",question=Question(id='relation',kind='choice',text='Given only the premise, is the hypothesis entailed, contradicted, or undetermined (neutral)?',labels=labels),gold=labels[r['label']],label_status='public',provenance=provenance(repo,'test',i)))
    repo='AmazonScience/massive';revision='ed58ac423a2f4121720918bf5301577edce4ffd3'
    script=file(repo,'massive.py').read_text(encoding='utf-8')
    labels=next(ast.literal_eval(n.value) for n in ast.parse(script).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='_INTENTS')
    datasets={};hashes={}
    for lang,locale in LANGS.items():
        name=f'{locale}/test/0000.parquet'
        path=hf_hub_download(repo,name,repo_type='dataset',revision=revision,local_dir=DATASETS/'raw'/'massive-converted')
        data=pq.read_table(path).to_pylist();datasets[lang]={str(r['id']):r for r in data};hashes[name]=digest(open(path,'rb').read())
        print(locale,len(data),flush=True)
    english=list(datasets['en'].values());ids=[str(english[i]['id']) for i in stratified(english,100,'intent')]
    for sid in ids:
        for lang in LANGS:
            r=datasets[lang][sid];gold=labels[r['intent']] if isinstance(r['intent'],int) else r['intent']
            cases.append(Case(id=f'massive-{sid}-{lang}',cluster=f'massive-{sid}',pack='Multilingual',family='MASSIVE',language=lang,state=r['utt'],question=Question(id='intent',kind='choice',text='Choose the intent of this assistant request.',labels=labels),gold=gold,label_status='public',provenance={**provenance(repo,'test',sid),'converted_revision':revision,'locale':LANGS[lang]}))
    save('multilingual',cases,1000);write_json(DATASETS/'massive-source-hashes.json',{'revision':revision,'files':hashes})
    rag()

if __name__=='__main__':run()
