"""Pure candidate-format helpers shared by the host and isolated workers."""
import json


def native_question(q):
    kind=q['kind']
    criteria=q.get('criteria')
    # Imported rubrics serialize these same criteria for the evidence UI. Keep
    # the original instructions when sending a native typed API request.
    instructions=q['text']
    if criteria is None:
        if q.get('rubric') not in (None,'','{}','[]','null'):instructions+='\n'+q['rubric']
        if kind=='noul':return {'type':kind,'instructions':instructions}
        criteria={x:x for x in q['labels']} if kind=='choice' else q['labels'] if kind=='score' else {'false':'no','true':'yes'}
    return {'type':kind,'instructions':instructions,'criteria':criteria}


def text(value):
    return value if isinstance(value,str) else json.dumps(value,ensure_ascii=False)


def normalize_answer(answer,q):
    if q['kind']=='noul':
        if isinstance(answer['noul'],bool):raise ValueError('Probability is boolean')
        value=float(answer['noul']);probs={'no':1-value,'yes':value}
    else:
        probs={str(k):float(v) for k,v in answer['probabilities'].items()}
        if q['kind']=='score':probs={label:probs[str(i)] for i,label in enumerate(q['labels'])}
    # Preserve a native decision if provided; a rounded vector may contain ties.
    return {'selected':answer.get('choice',max(probs,key=probs.get)),
            'probabilities':probs,'raw':answer}


def semif_row(case):
    q=case['question'];native=native_question(q);criteria=native.get('criteria')
    if q['kind']=='noul':
        options=[{'id':key,'description':key+': '+text((criteria or {}).get(key,f'The proposition is {key}.'))} for key in ('true','false')]
    elif q['kind']=='choice':
        values=criteria.items() if isinstance(criteria,dict) else ((v,v) for v in criteria)
        options=[{'id':key,'description':key+': '+text(value)} for key,value in values]
    else:
        # The author's frozen comparison excludes Score. This explicit Arena
        # extension applies the same categorical readout to ordered levels.
        options=[{'id':label,'description':label+': '+text(criteria[i])} for i,label in enumerate(q['labels'])]
    return {'id':case['case_id'],'state':case['state'],'question':native['instructions'],'options':options}


def capability_error(error):
    message=str(error).lower()
    return ('input tokens exceed limit' in message or
            ('longest prompt has' in message and 'tokens; limit is' in message))
