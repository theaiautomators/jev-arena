"""Two deterministic simulated workflows. No real-world actions or external tools."""
import random
from collections import deque
from arena.contracts import Case,Question

def distance(start,goal,blocked,size=6):
    queue=deque([(start,0)]);seen={start}
    while queue:
        (x,y),d=queue.popleft()
        if (x,y)==goal:return d
        for dx,dy in ((0,-1),(1,0),(0,1),(-1,0)):
            p=(x+dx,y+dy)
            if p not in seen and p not in blocked and 0<=p[0]<size and 0<=p[1]<size:seen.add(p);queue.append((p,d+1))
    return 999

class Warehouse:
    def __init__(self,seed):
        self.seed=seed;self.pos=(0,0);self.goal=(5,5);rng=random.Random(seed)
        self.blocked=set(rng.sample([(x,y) for x in range(1,5) for y in range(1,5)],5));self.steps=0;self.violations=0;self.trace=[]
    def case(self):
        labels=['north','east','south','west'];directions=[(0,-1),(1,0),(0,1),(-1,0)];scores=[]
        for dx,dy in directions:
            pos=(self.pos[0]+dx,self.pos[1]+dy)
            scores.append(distance(pos,self.goal,self.blocked) if 0<=pos[0]<6 and 0<=pos[1]<6 and pos not in self.blocked else 999)
        gold=labels[scores.index(min(scores))]
        state=f"Warehouse is a 6 by 6 grid. Coordinates x increase east and y increase south. Robot at {self.pos}; delivery goal {self.goal}; blocked cells {sorted(self.blocked)}. Stay within x=0..5,y=0..5; avoid blocked cells. Choose a move on a shortest route to the goal."
        return Case(id=f'warehouse-{self.seed}-{self.steps}',cluster=f'warehouse-{self.seed}',pack='Episodes',family='Warehouse',state=state,question=Question(id='move',kind='choice',text='What move should the robot make next?',labels=labels),gold=gold,acceptable=[labels[i] for i,v in enumerate(scores) if v==min(scores)])
    def step(self,p):
        before=self.pos;directions={'north':(0,-1),'east':(1,0),'south':(0,1),'west':(-1,0)}
        dx,dy=directions.get(p.selected,(0,0));after=(before[0]+dx,before[1]+dy)
        valid=p.status=='ok' and after not in self.blocked and 0<=after[0]<6 and 0<=after[1]<6
        if valid:self.pos=after
        else:self.violations+=1
        self.trace.append({'step':self.steps,'before':before,'after':self.pos,'answer':p.selected,'status':p.status,'request_ms':p.request_ms,'valid':valid});self.steps+=1
    @property
    def done(self):return self.pos==self.goal or self.steps>=40
    def result(self):return {'task':'warehouse','seed':self.seed,'success':self.pos==self.goal,'steps':self.steps,'violations':self.violations,'reward':int(self.pos==self.goal)*100-self.steps-self.violations*5,'blocked':sorted(self.blocked),'goal':self.goal,'trace':self.trace}

class Tickets:
    def __init__(self,seed):self.seed=seed;self.rng=random.Random(seed);self.steps=0;self.violations=0;self.correct=0;self.trace=[];self.current=None
    def case(self):
        topic=self.rng.choice(['payment','service outage','onboarding']);queue={'payment':'Billing','service outage':'Engineering','onboarding':'Success'}[topic];restricted=self.rng.random()<.25
        gold='Review' if restricted else queue
        self.current={'topic':topic,'restricted':restricted,'gold':gold}
        state=f"Ticket {self.seed}-{self.steps}: topic={topic}; account restricted={'yes' if restricted else 'no'}. Policy: restricted accounts must go to Review before any action. Otherwise payment goes to Billing, service outage to Engineering, onboarding to Success. Route the next ticket."
        return Case(id=f'tickets-{self.seed}-{self.steps}',cluster=f'tickets-{self.seed}',pack='Episodes',family='Ticket workflow',state=state,question=Question(id='route',kind='choice',text='Which queue should receive the ticket?',labels=['Billing','Engineering','Success','Review']),gold=gold)
    def step(self,p):
        good=p.status=='ok' and p.selected==self.current['gold'];self.correct+=good
        self.violations+=self.current['restricted'] and p.selected!='Review'
        self.trace.append({'step':self.steps,**self.current,'answer':p.selected,'correct':good,'request_ms':p.request_ms});self.steps+=1
    @property
    def done(self):return self.steps>=12
    def result(self):return {'task':'tickets','seed':self.seed,'success':self.correct==12,'steps':self.steps,'violations':self.violations,'reward':self.correct*10-self.violations*20,'trace':self.trace}

async def run_episodes(adapter,count,paid_cap,deadline_ms=None,on_progress=None):
    records=[]
    for cls in (Tickets,Warehouse):
        for seed in range(count//2):
            env=cls(5090+seed)
            while not env.done:
                pred=await adapter.predict(env.case(),paid_cap)
                missed=deadline_ms is not None and pred.request_ms>deadline_ms
                applied=pred.model_copy(update={'status':'timeout','selected':None}) if missed else pred
                env.step(applied);env.trace[-1]['deadline_missed']=missed
                env.trace[-1]['late_answer']=pred.selected if missed else None
            row=env.result();row['model_id']=adapter.id;row['mode']='deadline_500ms' if deadline_ms else 'untimed_quality';row['wall_request_ms']=sum(t['request_ms'] for t in row['trace']);row['deadline_ms']=deadline_ms;row['deadline_misses']=sum(t['deadline_missed'] for t in row['trace']) if deadline_ms else None
            records.append(row)
            if on_progress:on_progress(row)
    return records
