import { useState } from "react";
import catalog from "../../../docs/evidence/model-guide.json";
import taskData from "../../../docs/evidence/builder-task-breakdown.json";
import abcd from "../../../docs/evidence/abcd-dashboard-data.json";

const pct=(v:number|null|undefined)=>v==null?"Unavailable":(v*100).toFixed(2)+"%";
export function Takeaways({onModels,onAbcd}:{onModels:()=>void;onAbcd:()=>void}){
 return <section className="builder-takeaways"><div className="section-title"><div><h2>What builders should take away</h2><p>Choose for your workload, then test the complete workflow.</p></div></div>
 <div className="takeaway-list">
 <article><b>01</b><div><h3>Local can be fast and competitive</h3><p>Winnow and Decider were close to Jev on shared short-input questions. Local timing blocks were about 50–60 ms versus Jev’s 245 ms, including its network trip.</p></div></article>
 <article><b>02</b><div><h3>Small models can win a narrow job</h3><p>Laya led news classification here; Decider led multilingual entailment. A broad average can hide the best fit for your task.</p></div></article>
 <article><b>03</b><div><h3>Check input length and number of choices first</h3><p>A 16-choice interface cannot directly select among 77 intents. An 8K limit cannot fit our roughly 20K-token handbook. Some v2 8K limits were serving settings, not model limits.</p></div></article>
 <article><b>04</b><div><h3>More context is not automatically better</h3><p>In ABCD, Jev led full-handbook action selection; Winnow led the combined next-step task. Retrieval helped Winnow’s action selection. Long-input speed also reversed the short-input pattern.</p></div></article>
 <article><b>05</b><div><h3>Validate answers and confidence</h3><p>Correct choices can still fail a software output check. High confidence can be wrong. Keep validation, fallback handling and tests for repeated decisions in your application.</p></div></article>
 </div><div className="guide-actions"><button className="text-button" onClick={onModels}>Compare model requirements →</button><button className="text-button" onClick={onAbcd}>Explore the support-conversation test →</button></div>
 </section>
}
export function ModelGuide({selected,onSelect}:{selected:string|null;onSelect:(id:string)=>void}){
 const m=catalog.models.find(x=>x.id===selected)||catalog.models[0];
 return <><div className="results-select">{catalog.models.map(x=><button key={x.id} className={x.id===m.id?"selected":""} onClick={()=>onSelect(x.id)}>{x.name}</button>)}</div><section className="model-guide">
 <div className="section-title"><div><span className="eyebrow">{m.kind}</span><h2>{m.name}</h2><p>{m.note}</p></div>{m.url&&<a className="button secondary" href={m.url} target="_blank" rel="noreferrer">Official source ↗</a>}</div>
 <dl className="profile-grid">{[
 ["Parameters",m.size],["Built from",m.base],["Availability & license",m.weights],["Repository first created",m.repository_created||"Not verified"],["GPU memory after loading",m.loaded_gpu_gib==null?"Not recorded":m.loaded_gpu_gib+" GiB"],["Precision used",m.precision],["Context in our tests",m.context],["Choice limit",m.options],["Recorded load time",m.load_seconds==null?"Not applicable / not recorded":m.load_seconds+" seconds"]
 ].map(([k,v])=><div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
 <p className="small muted">{m.memory_note} System RAM was not measured. All local profiles ran on the same 32 GB RTX 5090; that does not prove they require a 32 GB GPU.</p><p className="small muted">{m.date_note} Base-model age and this decision model’s age are different. Sources checked {catalog.checked}; results use the saved revision below, not necessarily today’s latest release.</p><details className="explain"><summary>Exact evaluated version</summary><code>{m.revision}</code></details></section></>
}
const sources=[
 ["JevBench public","231","Public answer key","Decision, policy and reasoning questions.","https://github.com/fstandhartinger/jevbench"],
 ["Typed decisions","2,000","AI-generated reference answers","400 situations × five questions. Teacher agreement is separate from the headline score.","https://huggingface.co/datasets/LocalLLaMA/typed-decisions"],
 ["Classification","1,500","Public answer keys","500 each: sentiment (SST-2), news (AG News), banking intent (BANKING77).","https://huggingface.co/datasets/legacy-datasets/banking77"],
 ["Multilingual","1,000","Public answer keys","XNLI and MASSIVE, five languages. Related translations are not independent scenarios.","https://huggingface.co/datasets/facebook/xnli"],
 ["Document relevance","500","Public relevance labels","SciFact: whether a retrieved document is relevant to a claim. Many negatives; inspect ranking scores too.","https://huggingface.co/datasets/BeIR/scifact"],
 ["Arena policy tests","1,440","Answers calculated from explicit rules","Our generated cases across eight policy templates. Useful controlled checks, not broad human validation.",""],
 ["Changed-input checks","1,000","Answers calculated from explicit rules","Variations of the policy cases: rewording, distractions, reordered choices and changes that should change the answer.",""]
];
export function SourcesGuide(){
 return <section className="sources-guide"><h2>What makes up the 7,671 cases?</h2><p>JevBench is one source. Arena adds other datasets and controlled tests. This gives broader coverage, but does not make it a standardized replacement for those original benchmarks.</p>
 <div className="table-scroll"><table><thead><tr><th>Test group</th><th>Cases / model</th><th>Where the answer comes from</th><th>What it tests</th></tr></thead><tbody>{sources.map(([name,n,key,desc,url])=><tr key={name}><td>{url?<a href={url} target="_blank" rel="noreferrer">{name} ↗</a>:name}</td><td>{n}</td><td>{key}</td><td>{desc}</td></tr>)}</tbody></table></div>
 <p className="small muted">Additional original sources: <a href="https://huggingface.co/datasets/stanfordnlp/sst2" target="_blank" rel="noreferrer">SST-2</a> · <a href="https://huggingface.co/datasets/fancyzhx/ag_news" target="_blank" rel="noreferrer">AG News</a> · <a href="https://github.com/alexa/massive" target="_blank" rel="noreferrer">MASSIVE</a>. Exact samples and source revisions remain frozen in the evidence.</p>
 <h2>Answer key first; Astra is a separate spot-check</h2><p>5,671 questions per model have a public or rule-derived answer key. Code scores the selected answer and checks the output format. The other 2,000 compare against answers produced by AI teachers and are excluded from headline accuracy. The shared ranking uses the same 4,635 answer-key questions supported by all 13 profiles.</p><p>For completed v2, Astra reviewed 879 distinct answer pairs across 300 selected questions: 250 selected across test groups and 50 extra model-disagreement cases. Those reviews look for ambiguous questions and questionable answers. They do not contribute a percentage to headline accuracy and do not automatically change the answer key. No human validation is claimed.</p>
 <h2>ABCD is a second experiment</h2><p>300 held-out support conversations, five selected profiles, full handbook versus retrieved policy, and a separate simple long-context control. It asks a different question from v2 and was added later. Pooling it into the 13-profile total would give five models extra questions and impose an arbitrary task weighting. It belongs in the same dashboard with its own score.</p>
 <h2>Terms in plain English</h2><dl className="glossary">{[
 ["Answer accuracy · same questions","How often the model selected the answer-key label, using identical questions for every model. This is the simple comparison shown on the overview."],
 ["Correct + usable output","The answer is right AND the output passes Arena’s software checks, including probabilities adding to one within the declared tolerance. This was called strict accuracy."],
 ["Matched","The same questions for every model. It describes the comparison set, not another kind of answer."],
 ["Typical response time · P50","The median: half the measured requests were faster and half were slower. P95 is the point below which 95% finished."],
 ["Valid coverage","The fraction of all planned cases returning a usable output, whether right or wrong. Unsupported cases and failed requests lower it."],
 ["Teacher labels","Target answers produced by another AI model or an average of AI judgments. Agreement with them is not independent proof of correctness."],
 ["Changed-input checks · perturbations","Test whether small harmless edits preserve an answer, and whether changing a decisive fact changes the answer appropriately."],
 ["Confidence reliability","When a model says roughly 80% confidence, is it right roughly 80% of the time? Below the ideal line means overconfident; above means underconfident."]
 ].map(([k,v])=><div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
 </section>
}
function Value({value}:{value:unknown}){
 if(Array.isArray(value))return <ul>{value.map((v,i)=><li key={i}><Value value={v}/></li>)}</ul>;
 if(value!==null&&typeof value==="object")return <dl>{Object.entries(value).map(([k,v])=><div key={k}><dt>{k.replaceAll("_"," ")}</dt><dd><Value value={v}/></dd></div>)}</dl>;
 return <span>{String(value)}</span>
}
export function CaseState({text}:{text:string}){
 let parsed:unknown=null;try{parsed=JSON.parse(text)}catch{/* Text state. */}
 const parts=text.split(/(?=(?:Policy|Rubric|Claim|Document title|Document|Premise|Hypothesis|Proposed answer|Available tools|Source record|Query):)/g);
 return <div className="structured-state"><div className="field-label">Information given to every model</div><p className="small muted">A readable view of the saved input. These are sections of one input, not extra questions.</p>
 {parsed!==null&&typeof parsed==="object"?<Value value={parsed}/>:parts.filter(Boolean).map((s,i)=>{const m=s.match(/^([^:\n]{1,30}):\s*([\s\S]*)$/);return <section key={i}><h4>{m?m[1]:(parts.length>1?"Situation":"Input text")}</h4><p>{m?m[2]:s}</p></section>})}
 <details className="explain"><summary>Exact input text</summary><pre>{text}</pre></details></div>
}
const taskNames:Record<string,string>={"SST-2":"Sentiment · SST-2","AG News":"News topics · AG News","XNLI":"Statement agreement across languages · XNLI","SciFact":"Document relevance · SciFact","Arena Fresh":"Explicit policy rules","Robustness":"Changed-input checks"};
export function TaskBreakdown(){
 return <section className="analysis-panel"><h2>Different jobs, different strengths</h2><p>Answer-label accuracy on identical supported questions within each row. Descriptive results, not proof that small differences will generalize.</p><div className="table-scroll"><table><thead><tr><th>Task</th><th>Questions</th>{["jev","winnow","decider","nimble","plumb","laya"].map(id=><th key={id}>{catalog.models.find(x=>x.id===id)?.name}</th>)}</tr></thead><tbody>{Object.entries(taskData.groups).map(([k,g])=><tr key={k}><td>{taskNames[k]||k}</td><td>{g.n}</td>{["jev","winnow","decider","nimble","plumb","laya"].map(id=><td key={id}>{pct((g.scores as Record<string,number>)[id])}</td>)}</tr>)}</tbody></table></div><p className="small muted">SciFact’s first-option baseline scores 90.6% because most documents are irrelevant; plain accuracy hides that imbalance. Arena policy tests and their variations make up 2,440 of the 4,635 shared questions and use eight recurring templates. Public training exposure is unknown. Do not use this table as a deployment guarantee.</p></section>
}
export function ABCDResults(){
 const [condition,setCondition]=useState("full_handbook"),[task,setTask]=useState("combined"),[metric,setMetric]=useState("label");
 const models=abcd.models as unknown as Record<string,{natural:Record<string,Record<string,number|null>>;combined:Record<string,Record<string,number|null>>}>;
 const rows=Object.entries(models).map(([id,m])=>{const x=task==="combined"?m.combined[condition]:m.natural[condition+"/"+task];return {id,x}});
 return <section><h2>Support conversations · ABCD</h2><p>300 conversations. Five profiles. A separate follow-on to the 13-profile comparison. These are matches to recorded next steps, not live customer-resolution success.</p>
 <div className="abcd-controls"><label>Policy input<select value={condition} onChange={e=>setCondition(e.target.value)}><option value="full_handbook">Full handbook</option><option value="retrieved_policy">Retrieved policy</option></select></label><label>Task<select value={task} onChange={e=>setTask(e.target.value)}><option value="combined">Choose whether to act, speak or finish + correct action</option><option value="action">Choose an action when told an action is due</option><option value="route">Choose whether to act, speak or finish</option></select></label><label>Score<select value={metric} onChange={e=>setMetric(e.target.value)}><option value="label">Selected answer</option><option value="strict">Correct + usable output</option></select></label></div>
 <p className="score-note">{task==="action"?"300 action questions, all 30 options supplied.":"900 balanced checkpoints: 300 actions, 300 messages and 300 synthesized endings."} Unsupported capacity is shown separately.</p>
 <div className="family-bars">{rows.sort((a,b)=>Number(b.x[metric+"_accuracy_supported"]??-1)-Number(a.x[metric+"_accuracy_supported"]??-1)).map(({id,x})=><div key={id}><div><span>{catalog.models.find(m=>m.id===id)?.name||id}</span><strong>{pct(x[metric+"_accuracy_supported"])}</strong></div><div className="wide-track"><i style={{width:(Number(x[metric+"_accuracy_supported"]||0)*100)+"%"}}/></div><small>{String(x.supported??0)} supported · {String(x.unsupported??0)} unavailable</small></div>)}</div>
 <div className="takeaway-list"><article><b>→</b><div><h3>The ranking depends on the decision</h3><p>Winnow leads the combined balanced task. Jev leads full-handbook conditional action selection. Knowing when to speak is different from choosing the right action when told to act.</p></div></article><article><b>→</b><div><h3>Long inputs changed the speed comparison</h3><p>Full-handbook request medians were about 0.36s for hosted Jev, 1.57s for Qwen, 1.90s for Decider and 2.85s for Winnow. Retrieval greatly shortened local request times. Hardware, precision and caching differ.</p></div></article><article><b>→</b><div><h3>No unique long-context winner</h3><p>Jev, Winnow, Decider and Qwen selected all constructed labels in the easy context control. Nimble’s 8K release supported only the shortest condition. Decider had output-format failures despite correct labels.</p></div></article></div>
 <details className="explain"><summary>Scope, audit and cost</summary><p>12,720 saved records; 118 blinded answer reviews over 76 questions. All 33 flagged reviews inspected; gold unchanged. Automated review is not human validation. ABCD recorded Jev usage: $1.210811196; combined with v2: $1.458954042. Candidate window: 3h16m, excluding earlier wait/preflight and subsequent audit/reporting. No fine-tuning. Full evidence remains in the separate ABCD HTML/ZIP and report.</p></details></section>
}
