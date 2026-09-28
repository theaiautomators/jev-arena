from __future__ import annotations
import math
from collections import defaultdict
import numpy as np
from arena.contracts import Case, Prediction
from arena.config import digest


def statistical_clusters(cases):
    """Join related scenarios AND identical inputs before resampling clusters."""
    parents={c.cluster:c.cluster for c in cases};seen={}
    def root(cluster):
        while parents[cluster]!=cluster:
            parents[cluster]=parents[parents[cluster]];cluster=parents[cluster]
        return cluster
    for case in cases:
        key=digest({'state':case.state,'question':case.question.model_dump(exclude={'id'})})
        if key in seen:
            a,b=root(case.cluster),root(seen[key])
            if a!=b:parents[max(a,b)]=min(a,b)
        else:seen[key]=case.cluster
    return {case.id:root(case.cluster) for case in cases}

def validate_prediction(p: Prediction, case: Case) -> Prediction:
    if p.status != "ok": return p
    if p.selected not in case.question.labels:
        p.status,p.raw_valid,p.error="invalid",False,"Answer outside declared labels"
        return p
    if p.probabilities is not None:
        probs=p.probabilities
        if set(probs)!=set(case.question.labels) or any(not math.isfinite(v) or not 0<=v<=1 for v in probs.values()):
            p.status,p.raw_valid,p.error="invalid",False,"Invalid probability support or range"
        # Exactly rounded four-decimal vectors belong inside the 1e-4 boundary.
        # Binary addition can otherwise overshoot that boundary by about 1e-16.
        elif not math.isclose(math.fsum(probs.values()),1,rel_tol=0,abs_tol=1e-4+1e-12):
            p.status,p.raw_valid,p.error="invalid",False,"Probabilities do not sum to one"
        elif sum(probs.values())!=1:
            p.probabilities={k:v/sum(probs.values()) for k,v in probs.items()}
            p.normalized_rounding=True
    return p

def correct(case,p):
    return p["status"]=="ok" and p["selected"] in [case.gold,*case.acceptable]

def cluster_interval(values,clusters,seed=5090,repeats=10000):
    groups=defaultdict(list)
    for v,c in zip(values,clusters): groups[c].append(v)
    if not groups:return None
    sums=np.array([sum(g) for g in groups.values()]); counts=np.array([len(g) for g in groups.values()])
    rng=np.random.default_rng(seed)
    # Bounded memory: 10k x 7k direct draws would use hundreds of MB.
    means=[]
    for start in range(0,repeats,100):
        ids=rng.integers(0,len(sums),size=(min(100,repeats-start),len(sums)))
        means.extend((sums[ids].sum(1)/counts[ids].sum(1)).tolist())
    return [float(x) for x in np.quantile(means,[.025,.975])]

def summarize(cases:list[Case],predictions:list[dict],include_ci=True):
    clusters=statistical_clusters(cases) if include_ci else None
    lookup={c.id:c for c in cases}
    rows=[(lookup[p["case_id"]],p) for p in predictions if p["case_id"] in lookup]
    supported=[(c,p) for c,p in rows if p["status"]!="unsupported"]
    valid=[(c,p) for c,p in supported if p["status"]=="ok"]
    verified=[(c,p) for c,p in supported if c.label_status not in ("teacher","provisional")]
    teachers=[(c,p) for c,p in supported if c.label_status=="teacher"]
    scores=[int(correct(c,p)) for c,p in verified]
    # A post-hoc sensitivity diagnostic: never repairs the main fixed-contract score.
    label_scores=[int(p["selected"] in [c.gold,*c.acceptable]) for c,p in verified]
    contract_failures=sum(p['status']=='invalid' for c,p in verified)
    probrows=[(c,p) for c,p in verified if p["status"]=="ok" and p.get("probabilities")]
    bins=[{"lo":i/10,"hi":(i+1)/10,"count":0,"confidence":0.,"accuracy":0.} for i in range(10)]
    brier=defaultdict(list); nll=[]; ordinal=[]
    reference_brier=[sum((p['probabilities'][k]-c.reference_probs[k])**2 for k in p['probabilities']) for c,p in teachers if p['status']=='ok' and p.get('probabilities') and c.reference_probs]
    for c,p in probrows:
        probs=p["probabilities"]
        conf=probs[p["selected"]]
        bin=bins[min(9,int(conf*10))]
        bin["count"]+=1;bin["confidence"]+=conf;bin["accuracy"]+=correct(c,p)
        if c.reference_probs:
            reference_brier.append(sum((probs[k]-c.reference_probs[k])**2 for k in probs))
        else:
            v=(probs.get("yes",0)-int(c.gold=="yes"))**2 if c.question.kind=="noul" else sum((v-int(k==c.gold))**2 for k,v in probs.items())
            brier["binary" if c.question.kind=="noul" else "multiclass"].append(v)
            nll.append(-math.log(max(1e-12,probs[c.gold])))
        if c.question.kind=="score":
            values=list(map(float,c.question.labels)); span=max(values)-min(values)
            expected=sum(float(k)*v for k,v in probs.items())
            ordinal.append(abs(expected-float(c.gold))/span)
    for b in bins:
        if b["count"]: b["confidence"]/=b["count"];b["accuracy"]/=b["count"]
    ece=sum(b["count"]*abs(b["confidence"]-b["accuracy"]) for b in bins)/len(probrows) if probrows else None
    confusion=defaultdict(lambda:defaultdict(int)); family=defaultdict(lambda:{"total":0,"correct":0,"failed":0})
    for c,p in verified:
        f=family[c.pack]; f["total"]+=1;f["correct"]+=correct(c,p);f["failed"]+=p["status"]!="ok"
        # Namespace labels by task so unrelated label names do not merge.
        key=f"{c.pack}:{c.family}"
        confusion[key][(c.gold,p["selected"] if p["status"]=="ok" else "[failed]")]+=1
    fs=[]
    for cm in confusion.values():
        for label in {a for a,b in cm}:
            tp=cm.get((label,label),0);fp=sum(v for (a,b),v in cm.items() if b==label and a!=label);fn=sum(v for (a,b),v in cm.items() if a==label and b!=label)
            fs.append(2*tp/(2*tp+fp+fn) if (2*tp+fp+fn) else 0)
    lat=[p["request_ms"] for c,p in supported if p["status"]!="cancelled"]
    mean=lambda v:float(np.mean(v)) if v else None
    family_macro=mean([f['correct']/f['total'] for f in family.values() if f['total']])
    return {"planned":len(cases),"completed":len(rows),"supported":len(supported),"valid":len(valid),"verified_count":len(verified),"correct":sum(scores),"failed":len(supported)-len(valid),"unsupported":len(rows)-len(supported),"accuracy":mean(scores),"selected_label_accuracy":mean(label_scores),"selected_label_correct":sum(label_scores),"output_contract_failures":contract_failures,"pack_macro_accuracy":family_macro,"coverage":len(valid)/len(cases) if cases else 0,"valid_rate":len(valid)/len(supported) if supported else None,"macro_f1":mean(fs),"accuracy_ci":cluster_interval(scores,[clusters[c.id] for c,p in verified]) if include_ci else None,"p50_ms":float(np.median(lat)) if lat else None,"p95_ms":float(np.quantile(lat,.95)) if lat else None,"brier_binary":mean(brier["binary"]),"brier_multiclass":mean(brier["multiclass"]),"teacher_agreement":mean([int(correct(c,p)) for c,p in teachers]),"teacher_brier":mean(reference_brier),"nll":mean(nll),"ece":ece,"ordinal_mae":mean(ordinal),"reliability":bins,"families":dict(family),"probability_count":len(probrows),"teacher_count":len(teachers),"confusion":{task:[{"reference":a,"predicted":b,"count":v} for (a,b),v in cm.items()] for task,cm in confusion.items()},"latency_scope":"all attempted quality requests, including failures; excludes warmup","diagnostics":diagnostics(cases,rows)}

def paired(cases,a,b):
    am={p["case_id"]:p for p in a};bm={p["case_id"]:p for p in b}
    cohort=[c for c in cases if c.label_status not in ("teacher","provisional") and c.id in am and c.id in bm and am[c.id]["status"]!="unsupported" and bm[c.id]["status"]!="unsupported"]
    clusters=statistical_clusters(cases)
    diffs=[int(correct(c,am[c.id]))-int(correct(c,bm[c.id])) for c in cohort]
    return {"n":len(cohort),"delta":float(np.mean(diffs)) if diffs else None,"ci":cluster_interval(diffs,[clusters[c.id] for c in cohort])}

def diagnostics(cases,rows):
    """Secondary metrics retain task denominators and never backfill missing scores."""
    mean=lambda xs:float(np.mean(xs)) if xs else None
    by_id={c.id:(c,p) for c,p in rows}
    verified=[(c,p) for c,p in rows if c.label_status not in ('teacher','provisional') and p['status']=='ok']
    binary=[(int(c.gold=='yes'),p['probabilities']['yes']) for c,p in verified if c.question.kind=='noul' and p.get('probabilities')]
    # Mann–Whitney statistic with half credit for ties, per binary task family.
    aucs={}
    for task in sorted({c.pack+':'+c.family for c,p in verified if c.question.kind=='noul'}):
        pairs=[(int(c.gold=='yes'),p['probabilities']['yes']) for c,p in verified if c.question.kind=='noul' and c.pack+':'+c.family==task and p.get('probabilities')]
        pos=np.array([v for y,v in pairs if y]);neg=np.array([v for y,v in pairs if not y])
        if len(pos) and len(neg):aucs[task]=float(((pos[:,None]>neg).sum()+.5*(pos[:,None]==neg).sum())/(len(pos)*len(neg)))
    curves=[]
    probabilistic=[(c,p) for c,p in verified if p.get('probabilities')]
    for threshold in (0,.5,.6,.7,.8,.9,.95,.99):
        accepted=[(c,p) for c,p in probabilistic if p['probabilities'][p['selected']]>=threshold]
        curves.append({'threshold':threshold,'accepted':len(accepted),'coverage':len(accepted)/len(cases) if cases else 0,'error':mean([not correct(c,p) for c,p in accepted])})
    robust=defaultdict(list)
    for c,p in rows:
        anchor=by_id.get(c.provenance.get('anchor_id'))
        if c.variant and anchor and p['status']!='unsupported' and anchor[1]['status']!='unsupported':
            a,ap=anchor
            robust[c.variant].append({'delta':int(correct(c,p))-int(correct(a,ap)),'flip':p['selected']!=ap['selected'],'sensitive':correct(c,p) and correct(a,ap)})
    ranking=defaultdict(list)
    for c,p in verified:
        if c.family=='SciFact' and p.get('probabilities'):
            ranking[c.cluster].append((c,p))
    ranks=[]
    for cluster,group in ranking.items():
        expected=sum(c.cluster==cluster for c in cases)
        if len(group)!=expected:continue
        ordered=sorted(group,key=lambda cp:-cp[1]['probabilities'].get('yes',0))
        rel=[int(c.gold=='yes') for c,p in ordered];ideal=sorted(rel,reverse=True)
        dcg=lambda vs:sum(v/math.log2(i+2) for i,v in enumerate(vs[:10]))
        denom=dcg(ideal)
        ranks.append({'query':cluster,'ndcg_at_10':dcg(rel)/denom if denom else None,'mrr':next((1/(i+1) for i,v in enumerate(rel) if v),0),'relevant_in_pool':sum(rel)})
    return {'binary_auroc_by_task':aucs,'coverage_error':curves,'coverage_error_note':'Descriptive test-set thresholds, not calibrated deployment operating points.','robustness':{k:{'pairs':len(v),'accuracy_delta':mean([x['delta'] for x in v]),'answer_flip_rate':mean([x['flip'] for x in v]),'both_correct':mean([x['sensitive'] for x in v])} for k,v in robust.items()},'rag':{'queries':len(ranks),'ndcg_at_10':mean([r['ndcg_at_10'] for r in ranks if r['ndcg_at_10'] is not None]),'mrr':mean([r['mrr'] for r in ranks]),'note':'Reranking within fixed BM25 pools; zero-positive pools excluded from nDCG, included as zero in MRR.','per_query':ranks}}
