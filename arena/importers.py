"""Pinned, source-preserving public benchmark importers. Never executes dataset scripts."""
from __future__ import annotations
import ast
import csv
import io
import json
import math
import random
import re
import tarfile
import urllib.request
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download,HfApi
from arena.config import DATASETS,ROOT,digest,write_json
from arena.contracts import Case,Question

PINS={
 "LocalLLaMA/typed-decisions":"f7a2487edd7a043a5441a5e9ccc7fe5ddbd9ebe8",
 "stanfordnlp/sst2":"8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb",
 "fancyzhx/ag_news":"eb185aade064a813bc0b7f42de02595523103ca4",
 "legacy-datasets/banking77":"f54121560de48f2852f90be299010d1d6dc612ec",
 "AmazonScience/massive":"ff6bd8e4b27c3543e4f8fe2108f32bb95a6f8740",
 "facebook/xnli":"b8dd5d7af51114dbda02c0e3f6133f332186418e",
 "BeIR/scifact":"b3b5335604bf5ee3c4447671af975ea25143d4f5",
 "BeIR/scifact-qrels":"2938d17dc3b09882fdb8c12bbbe2e2dc0e75a029",
}
LANGS={"en":"en-US","es":"es-ES","de":"de-DE","hi":"hi-IN","ar":"ar-SA"}

def file(repo,name):
    return Path(hf_hub_download(repo,name,repo_type="dataset",revision=PINS[repo],local_dir=DATASETS/"raw"/repo.replace("/","--")))

def parquet(repo,name):return pq.read_table(file(repo,name)).to_pylist()

def provenance(repo,split,index):return {"source":f"https://huggingface.co/datasets/{repo}","revision":PINS[repo],"source_split":split,"source_index":index,"sampling_seed":5090,"redistribution":"download from original source"}

def stratified(rows,count,key="label"):
    groups=defaultdict(list)
    for i,row in enumerate(rows):groups[row[key]].append(i)
    rng=random.Random(5090)
    for ids in groups.values():rng.shuffle(ids)
    selected=[]
    keys=sorted(groups,key=str)
    while len(selected)<count:
        changed=False
        for k in keys:
            if groups[k]:selected.append(groups[k].pop());changed=True
            if len(selected)==count:break
        if not changed:raise ValueError("Insufficient rows for stratified sample")
    return sorted(selected)

def save(pack,cases,expected):
    if len(cases)!=expected:raise ValueError(f"{pack}: expected {expected}, got {len(cases)}")
    if len({c.id for c in cases})!=len(cases):raise ValueError("Duplicate source IDs")
    raw="\n".join(c.model_dump_json() for c in cases)+"\n"
    path=DATASETS/f"{pack}-cases.jsonl";temp=path.with_suffix(".tmp");temp.write_text(raw,encoding="utf-8");temp.replace(path)
    write_json(DATASETS/f"{pack}-manifest.json",{"version":"arena-v1","count":len(cases),"sha256":digest(raw.encode()),"source_revisions":PINS,"case_ids":[c.id for c in cases]})
    print(f"{pack}: {len(cases)} cases frozen",flush=True)

def classification():
    cases=[]
    repo="legacy-datasets/banking77"
    # Read declared class ordering from the original card, not alphabetical guesses.
    import yaml
    card=file(repo,"README.md").read_text(encoding="utf-8")
    meta=yaml.safe_load(card.split("---",2)[1]);features=meta["dataset_info"]["features"]
    names=next(f for f in features if f["name"]=="label")["dtype"]["class_label"]["names"]
    banking=[names[str(i)] if str(i) in names else names[i] for i in range(77)]
    specs=[("stanfordnlp/sst2","validation","SST-2",["negative","positive"],"sentence","What sentiment does this movie review express?"),("fancyzhx/ag_news","test","AG News",["World","Sports","Business","Sci/Tech"],"text","Which news category best describes this article?"),(repo,"test","BANKING77",banking,"text","Which banking intent best describes this customer request?")]
    for repo,split,family,labels,textkey,prompt in specs:
        rows=parquet(repo,f"data/{split}-00000-of-00001.parquet")
        for i in stratified(rows,500):
            row=rows[i];cid=f"classification-{family.lower()}-{i}"
            cases.append(Case(id=cid,cluster=cid,pack="Classification",family=family,state=row[textkey],question=Question(id="label",kind="choice",text=prompt,labels=labels),gold=labels[row["label"]],label_status="public",provenance=provenance(repo,split,i)))
    save("classification",cases,1500)

def typed_decisions():
    repo="LocalLLaMA/typed-decisions";rows=parquet(repo,"all/test-00000-of-00001.parquet");cases=[]
    if len(rows)!=400:raise ValueError("Unexpected typed-decisions test split size")
    for i,row in enumerate(rows):
        questions=json.loads(row["questions"])
        for qid,q in questions.items():
            probs=json.loads(row["gold"])[qid]["probabilities"]
            if q["type"]=="noul":probs={"no":probs["false"],"yes":probs["true"]}
            labels=list(probs)
            case=Case(id=f"typed-{row['id']}-{qid}",cluster="typed-"+row["id"],pack="Typed decisions",family=row["workflow"],state=row["state"],question=Question(id=qid,text=q["instructions"],kind=q["type"],labels=labels,rubric=json.dumps(q.get("criteria",{}),ensure_ascii=False),criteria=q.get('criteria')),gold=max(probs,key=probs.get),reference_probs=probs,label_status="teacher",provenance={**provenance(repo,"test",i),"native_question":q,"reference_basis":"averaged teacher probabilities, not independent human truth"})
            case.question.criteria=q.get("criteria")
            cases.append(case)
    save("typed",cases,2000)

def multilingual():
    cases=[];repo="facebook/xnli";rows=parquet(repo,"all_languages/test-00000-of-00001.parquet");labels=["entailment","neutral","contradiction"]
    for i in stratified(rows,100):
        row=rows[i];hyp=dict(zip(row["hypothesis"]["language"],row["hypothesis"]["translation"]))
        for lang in LANGS:
            cid=f"xnli-{i}-{lang}"
            cases.append(Case(id=cid,cluster=f"xnli-{i}",pack="Multilingual",family="XNLI",language=lang,state=f"Premise: {row['premise'][lang]}\nHypothesis: {hyp[lang]}",question=Question(id="relation",kind="choice",text="Given only the premise, is the hypothesis entailed, contradicted, or undetermined (neutral)?",labels=labels),gold=labels[row["label"]],label_status="public",provenance=provenance(repo,"test",i)))
    # Download official archive. Parse just five locale files in memory, no extraction.
    repo="AmazonScience/massive";script=file(repo,"massive.py").read_text(encoding="utf-8")
    parsed=ast.parse(script);values={}
    for node in parsed.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ("_URL1","_INTENTS"):
            values[node.targets[0].id]=ast.literal_eval(node.value)
    archive=DATASETS/"raw"/"massive-1.1.tar.gz";archive.parent.mkdir(parents=True,exist_ok=True)
    if not archive.exists():
        urllib.request.urlretrieve(values["_URL1"],archive.with_suffix(".download"));archive.with_suffix(".download").replace(archive)
    datasets={}
    with tarfile.open(archive,"r:gz") as tf:
        for member in tf:
            if not member.isfile():continue
            locale=Path(member.name).name.removesuffix(".jsonl")
            if locale not in LANGS.values():continue
            rows=[json.loads(s) for s in tf.extractfile(member).read().decode().splitlines()]
            datasets[locale]={str(r["id"]):r for r in rows if r["partition"]=="test"}
    if len(datasets)!=5:raise ValueError("Official MASSIVE archive missing requested locales")
    labels=values["_INTENTS"];english=list(datasets["en-US"].values());ids=[str(english[i]["id"]) for i in stratified(english,100,"intent")]
    archive_hash=digest(archive.read_bytes())
    for source_id in ids:
        for lang,locale in LANGS.items():
            row=datasets[locale][source_id];cid=f"massive-{source_id}-{lang}"
            cases.append(Case(id=cid,cluster=f"massive-{source_id}",pack="Multilingual",family="MASSIVE",language=lang,state=row["utt"],question=Question(id="intent",kind="choice",text="Choose the intent of this assistant request.",labels=labels),gold=row["intent"],label_status="public",provenance={**provenance(repo,"test",source_id),"archive_url":values["_URL1"],"archive_sha256":archive_hash,"locale":locale}))
    save("multilingual",cases,1000)

def rag():
    repo="BeIR/scifact";corpus=parquet(repo,"corpus/corpus-00000-of-00001.parquet");queries=parquet(repo,"queries/queries-00000-of-00001.parquet");qrels=defaultdict(dict)
    with file("BeIR/scifact-qrels","test.tsv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle,delimiter="\t"):qrels[row["query-id"]][row["corpus-id"]]=int(row["score"])
    qmap={r["_id"]:r for r in queries};rng=random.Random(5090);ids=sorted(rng.sample(sorted(qrels),50))
    tokenize=lambda s:re.findall(r"\w+",s.lower())
    tokens=[Counter(tokenize(r["title"]+" "+r["text"])) for r in corpus];lengths=np.array([sum(t.values()) for t in tokens]);avg=lengths.mean();df=Counter(t for doc in tokens for t in doc);postings=defaultdict(list)
    for i,doc in enumerate(tokens):
        for word,tf in doc.items():postings[word].append((i,tf))
    cases=[];recalls=[];manifest=[]
    for qid in ids:
        query=qmap[qid]["text"];scores=np.zeros(len(corpus))
        for word in set(tokenize(query)):
            idf=math.log(1+(len(corpus)-df[word]+.5)/(df[word]+.5))
            for i,tf in postings[word]:scores[i]+=idf*tf*2.5/(tf+1.5*(.25+.75*lengths[i]/avg))
        pool=sorted(range(len(corpus)),key=lambda i:(-scores[i],corpus[i]["_id"]))[:10];relevant={k for k,v in qrels[qid].items() if v>0};hit={corpus[i]["_id"] for i in pool}&relevant;recalls.append(len(hit)/len(relevant))
        manifest.append({"query_id":qid,"pool":[corpus[i]["_id"] for i in pool],"pool_recall":recalls[-1]})
        for rank,i in enumerate(pool):
            doc=corpus[i];cid=f"scifact-{qid}-{doc['_id']}";gold="yes" if doc["_id"] in relevant else "no"
            cases.append(Case(id=cid,cluster="scifact-"+qid,pack="RAG relevance",family="SciFact",state=f"Claim: {query}\nDocument title: {doc['title']}\nDocument: {doc['text']}",question=Question(id="relevance",kind="noul",text="Does this document provide relevant evidence for verifying or refuting the claim?",labels=["no","yes"]),gold=gold,label_status="public",provenance={**provenance(repo,"test",doc["_id"]),"query_id":qid,"pool_rank":rank+1,"bm25_score":float(scores[i]),"qrel":qrels[qid].get(doc["_id"],0),"unjudged_assumption":"Unjudged pool documents follow BEIR non-relevant convention; not independently audited"}))
    save("rag",cases,500);write_json(DATASETS/"rag-pools.json",{"retriever":"BM25 k1=1.5 b=0.75 lowercase Unicode word tokenizer","mean_pool_recall":float(np.mean(recalls)),"queries":manifest})

def prepare_all():
    from arena.multilingual import run as finish
    for fn in (classification,typed_decisions,finish):fn()

if __name__=="__main__":prepare_all()
