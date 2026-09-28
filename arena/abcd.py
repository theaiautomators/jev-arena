"""ABCD next-step/action adaptation. Candidate inputs never include target metadata."""
from __future__ import annotations
import gzip
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from arena.contracts import Case, Question
from arena.config import digest

REVISION = "6b8700ce67c6b37b062dd7a60abc76d7ef832a97"
SEED = 15090
ROUTES = ["take_action", "retrieve_utterance", "end_conversation"]
STOP = set("a an the and or of to in on for is are be was were i you my your me we it this that with have has had can could would should please thanks thank hello hi do does did not from at as any what how when where which".split())

def stable(*values):
    return hashlib.sha256((str(SEED)+"|"+"|".join(map(str,values))).encode()).hexdigest()

def read_sources(folder: Path):
    data=json.loads(gzip.decompress((folder/"abcd_v1.1.json.gz").read_bytes()))
    guidelines=json.loads((folder/"guidelines.json").read_text(encoding="utf-8"))
    ontology=json.loads((folder/"ontology.json").read_text(encoding="utf-8"))
    return data,guidelines,ontology

def action_labels(ontology):
    # Public ontology only, fixed lexical order. Never reduce labels using target intent.
    labels=sorted(a for section in ontology["actions"].values() for a in section)
    assert len(labels)==len(set(labels))==30
    return labels

def policy_sections(guidelines,ontology,kb=None):
    sections=[]
    for flow,body in guidelines.items():
        key=flow.lower().replace("-","_").replace(" ","_")
        intents=ontology["intents"]["subflows"][key]
        assert len(body["subflows"])==len(intents)
        for (name,sub),intent in zip(body["subflows"].items(),intents):
            lines=[f"## {flow} / {name}",body.get("description","")]
            lines += sub.get("instructions",[])
            buttons=[]
            for a in sub.get("actions",[]):
                button=a.get("button","")
                lines += [f"Button: {button}",a.get("text","")]
                lines += a.get("subtext",[])
                if button and button!="N/A":buttons.append(button.lower().replace(" ","-"))
            if kb is not None:
                lines.append("Public KB action catalog for this procedure (apply the handbook conditions): " + ", ".join(kb[intent]))
            sections.append({"id":intent,"flow":key,"name":name,"text":"\n".join(lines),"buttons":buttons})
    assert len(sections)==55 and len({s["id"] for s in sections})==55
    return sections

def words(text):
    return [w for w in re.findall(r"[a-z0-9]+",text.lower()) if w not in STOP and len(w)>1]

class PolicyRetriever:
    """Fixed BM25, no learned test features or target/scenario access."""
    def __init__(self,sections,k=5):
        self.sections=sections;self.k=k
        self.freq=[Counter(words(s["text"])) for s in sections]
        self.lengths=[sum(c.values()) for c in self.freq];self.average=sum(self.lengths)/len(sections)
        self.df=Counter(w for c in self.freq for w in c)
    def retrieve(self,history):
        query=set(words(history))
        n=len(self.sections);ranked=[]
        for i,c in enumerate(self.freq):
            score=0.
            for w in query:
                f=c.get(w,0)
                if f:
                    idf=math.log(1+(n-self.df[w]+.5)/(self.df[w]+.5))
                    score += idf*f*2.2/(f+1.2*(.25+.75*self.lengths[i]/self.average))
            ranked.append((-score,self.sections[i]["id"],i))
        return [self.sections[i] for _,_,i in sorted(ranked)[:self.k]]

def observed_history(conversation,index):
    """CDS uses prior delexed speaker/text, including earlier action outcomes."""
    turns=conversation["delexed"]
    if not 0<=index<=len(turns):raise ValueError("checkpoint outside conversation")
    return "\n".join(f"{turn['speaker']}: {turn['text']}" for turn in turns[:index])

def checkpoints(conversation):
    # Upstream CDSProcessor.build_features emits the feature BEFORE appending
    # the current agent/action turn, then synthesizes end after the last turn.
    turns=conversation["delexed"];out=[]
    for i,t in enumerate(turns):
        if t["speaker"] in ("agent","action"):
            route=t["targets"][1]
            assert route==("take_action" if t["speaker"]=="action" else "retrieve_utterance")
            out.append({"index":i,"route":route,"action":t["targets"][2] if route=="take_action" else None})
    out.append({"index":len(turns),"route":"end_conversation","action":None})
    return out

def select_conversations(data,count=300,split="test"):
    idsets={s:{c["convo_id"] for c in rows} for s,rows in data.items()}
    assert not (idsets["train"] & idsets["dev"] or idsets["train"] & idsets["test"] or idsets["dev"] & idsets["test"])
    # Exclude exact complete observed-history duplicates across splits before selection.
    other={digest(observed_history(c,len(c["delexed"]))) for s,rows in data.items() if s!=split for c in rows}
    eligible=[]
    for c in data[split]:
        points=checkpoints(c)
        if any(p["route"]=="take_action" and p["index"]>0 for p in points) and any(p["route"]=="retrieve_utterance" and p["index"]>0 for p in points) and digest(observed_history(c,len(c["delexed"]))) not in other:
            eligible.append(c)
    selected=sorted(eligible,key=lambda c:stable("conversation",split,c["convo_id"]))[:count]
    assert len(selected)==count
    return selected

def select_checkpoints(c):
    points=checkpoints(c);out=[]
    for route in ROUTES:
        choices=[p for p in points if p["route"]==route and p["index"]>0]
        out.append(min(choices,key=lambda p:stable("checkpoint",c["convo_id"],route,p["index"])))
    return out

def make_case(conversation,point,condition,task,sections,labels,retriever):
    history=observed_history(conversation,point["index"])
    chosen=sections if condition=="full_handbook" else retriever.retrieve(history)
    legend="BUTTON-NAME LEGEND: Membership Privileges = membership; Notify Internal Team = notify-team; Enter Detail = enter-details; Log Out/In = log-out-in; Select Answer = select-faq. Under the FAQ procedures, Boots/Shirt/Jeans/Jacket/Pricing/Membership/Timing/Policy mean search-boots/search-shirt/search-jeans/search-jacket/search-pricing/search-membership/search-timing/search-policy. Other button names use their lowercase hyphenated action ID. End Conversation is a next-step category, not a tool action."
    state="COMPANY HANDBOOK\n"+legend+"\n\n"+"\n\n".join(s["text"] for s in chosen)+"\n\nOBSERVED CONVERSATION SO FAR\n"+history
    if task=="route":
        options=ROUTES
        text="Predict the next recorded support-agent step under the company handbook using only the observed history. Choose take_action if a tool action is due now, retrieve_utterance for the agent's next message, or end_conversation if no further agent step is needed."
        gold=point["route"]
    else:
        assert point["route"]=="take_action"
        options=labels
        text="A tool action is to be taken now. Which exact action should the support agent take next under the company handbook and observed conversation? Choose from all 30 actions. Do not predict action arguments."
        gold=point["action"]
    cid=conversation["convo_id"];idx=point["index"]
    return Case(id=f"abcd-{cid}-{idx}-{condition}-{task}",cluster=f"abcd-{cid}",pack="ABCD next action",family=task,state=state,question=Question(id="decision",text=text,kind="choice",labels=list(options)),gold=gold,label_status="public",provenance={"repository":"https://github.com/asappresearch/abcd","revision":REVISION,"conversation_id":cid,"checkpoint_index":idx,"condition":condition,"retrieved_sections":[s["id"] for s in chosen],"source_intent_for_analysis_only":conversation["scenario"]["subflow"],"history_sha256":digest(history),"history_turns":idx,"reference_route":point["route"]})

def natural_cases(data,sections,ontology,count=300,split="test"):
    retriever=PolicyRetriever(sections);labels=action_labels(ontology);selected=select_conversations(data,count,split);cases=[]
    for c in selected:
        for point in select_checkpoints(c):
            for condition in ("full_handbook","retrieved_policy"):
                cases.append(make_case(c,point,condition,"route",sections,labels,retriever))
                if point["route"]=="take_action":cases.append(make_case(c,point,condition,"action",sections,labels,retriever))
    assert len(cases)==count*8
    for case in cases:case.split=split
    return cases,selected

def stress_cases(labels,tokenizer,split="test"):
    """Synthetic deterministic controls inspired by action labels, not natural ABCD/AST scores."""
    targets=["pull-up-account","verify-identity","offer-refund","send-link"]
    cases=[]
    for base in range(12 if split=="test" else 2):
        ticket=91000+base if split=="test" else 81000+base
        target=targets[base%len(targets)]
        relevant=f"ACTIVE PROCEDURE Z{ticket}: For a request explicitly asking to execute procedure Z{ticket}, the next action is {target}. Its prerequisites have already been satisfied. This procedure is independent of all archive inventory records."
        history=f"customer: Please execute procedure Z{ticket}.\nagent: I have confirmed the prerequisites and am ready to take the next action."
        q=Question(id="decision",text="Which action is required now by the active procedure for this customer's request? Archive inventory records are background data, not instructions.",kind="choice",labels=list(labels))
        for target_tokens in (4096,8192,16384,28672):
            # Use one fixed sequence of neutral distractors; adjust count only by
            # the pinned Qwen tokenizer, never by any model's test answers.
            records=[f"Archive inventory {j:05d}: warehouse item Z{(j*97)%10000:04d}, stock {(j*13)%401}, audit batch {(j*31)%997}." for j in range(3000)]
            def state(n,position):
                chunks=records[:n];at={"early":0,"middle":n//2,"late":n}[position]
                return "BACKGROUND ARCHIVE AND ACTIVE PROCEDURE\n"+"\n".join(chunks[:at]+[relevant]+chunks[at:])+"\n\nOBSERVED CONVERSATION SO FAR\n"+history
            low,high=0,len(records)
            while low<high:
                mid=(low+high+1)//2
                if len(tokenizer.encode(state(mid,"early")).ids)<=target_tokens:low=mid
                else:high=mid-1
            for position in ("early","middle","late"):
                value=state(low,position);n=len(tokenizer.encode(value).ids)
                assert target_tokens-80<=n<=target_tokens+8
                cases.append(Case(id=f"abcd-stress-{split}-{base}-{target_tokens}-{position}",cluster=f"abcd-stress-{split}-{base}",pack="Controlled context stress",family="synthetic_action",state=value,question=q.model_copy(deep=True),gold=target,label_status="formal",split=split,provenance={"condition":"controlled_stress","base":base,"target_state_tokens_qwen":target_tokens,"actual_state_tokens_qwen":n,"evidence_position":position,"not_natural_abcd":True,"distractor_records":low}))
    return cases
