import { useEffect, useState } from "react";
import type { Case, Prediction, Result } from "./types";
import { CaseState } from "./Guide";
import { useViewState } from "./ViewHistory";
import savedAnalysis from "../../../docs/evidence/video-task-analysis.json";
import findings from "../../../docs/evidence/video-findings.json";

export type CaseJump = { pack: string; family: string; model?: string; search?: string };
type Counts = { n: number; planned: number; label_correct: number; strict_correct: number;
  label_accuracy: number | null; strict_accuracy: number | null; failed: number; invalid: number;
  unsupported: number; missing: number; p50_ms: number | null; p95_ms: number | null };
type Group = { key: string; pack: string; family: string; cases: number; reference_n: number;
  shared_n: number; teacher_n: number; models: Record<string, Record<string, Counts>> };
type Analysis = { run_id: string; groups: Group[]; models: string[]; shared_reference_n: number };
type Facet = { pack: string; family: string; count: number };
type CaseIndex = { total: number; cases: (Case & { preview: string })[]; facets: Facet[] };
const names: Record<string, string> = {"AG News": "News topics · AG News", "SST-2": "Sentiment · SST-2",
  BANKING77: "Banking intents · 77 choices", XNLI: "Multilingual entailment · XNLI", MASSIVE: "Multilingual intent · MASSIVE",
  SciFact: "Document relevance · SciFact", "Arena Fresh": "Explicit policy rules", Robustness: "Changed-input checks"};
const title = (pack: string, family: string) => names[family] || family || names[pack] || pack || "All question types";
const percent = (v: number | null) => v == null ? "Unavailable" : `${(v * 100).toFixed(2)}%`;
const time = (v: number | null) => v == null ? "—" : `${Math.round(v).toLocaleString()} ms`;
const cache = new Map<string, unknown>();
async function read<T>(path: string, signal: AbortSignal, immutable: boolean): Promise<T> {
  if (immutable && cache.has(path)) return cache.get(path) as T;
  const r = await fetch(`/api${path}`, { signal });
  if (!r.ok) throw new Error((await r.json()).detail || `Request failed (${r.status})`);
  const data = await r.json();
  if (immutable) { if (cache.size >= 60) cache.delete(cache.keys().next().value!); cache.set(path, data); }
  return data;
}

export function TaskAnalysis({ result, onCases }: { result: Result; onCases: (jump: CaseJump) => void }) {
  const [data, setData] = useState<Analysis | null>(null), [error, setError] = useState("");
  const [groupKey, setGroupKey] = useViewState(`analysis:${result.run_id}:group`, "::"), [model, setModel] = useViewState(`analysis:${result.run_id}:model`, "");
  const [scope, setScope] = useViewState(`analysis:${result.run_id}:scope`, "shared"), [metric, setMetric] = useViewState(`analysis:${result.run_id}:metric`, "label");
  useEffect(() => {
    const abort = new AbortController(); setData(null); setError("");
    if (window.__ARENA_REPORT__) {
      if (result.run_id === savedAnalysis.run_id) setData(savedAnalysis as Analysis);
      else setError("Open the local Arena app to explore question types for this saved report.");
    } else read<Analysis>(`/runs/${result.run_id}/analysis`, abort.signal, result.status === "complete")
      .then(d => { if (!abort.signal.aborted) setData(d); }).catch(e => { if (!abort.signal.aborted) setError(String(e.message)); });
    return () => abort.abort();
  }, [result.run_id, result.status]);
  const group = data?.groups.find(g => g.key === groupKey) || data?.groups[0];
  const noSharedQuestions = !!group?.reference_n && !group.shared_n;
  const activeScope = group?.reference_n === 0 && group.teacher_n ? "teacher" : noSharedQuestions && scope === "shared" ? "supported" : scope;
  const rows = result.entrants.filter(e => !model || e.id === model).map(e => ({ ...e, counts: group?.models[e.id]?.[activeScope] }))
    .filter(e => e.counts).sort((a, b) => ((b.counts![`${metric}_accuracy` as keyof Counts] as number | null) ?? -1) - ((a.counts![`${metric}_accuracy` as keyof Counts] as number | null) ?? -1));
  const lead = rows[0], leadScore = lead?.counts?.[`${metric}_accuracy` as keyof Counts] as number | null | undefined;
  return <section className="task-analysis" aria-label="Results by question type">
    <div className="section-title"><div><h2>Results by question type</h2><p>Compare every model on one job, or inspect one model across jobs.</p></div></div>
    {error && <p role="alert">{error}</p>}{!data && !error && <p role="status">Loading saved analysis…</p>}
    {data && group && <>
      <div className="quick-types" aria-label="Jump to question type">{[["", ""], ["Classification", "AG News"], ["Classification", "SST-2"], ["Classification", "BANKING77"], ["Multilingual", "XNLI"], ["Arena Fresh", ""], ["RAG relevance", "SciFact"]].filter(([p, f]) => data.groups.some(g => g.key === `${p}::${f}`)).map(([p, f]) => <button key={p+f} aria-pressed={group.key === `${p}::${f}`} className={group.key === `${p}::${f}` ? "selected" : ""} onClick={() => setGroupKey(group.key === `${p}::${f}` ? "::" : `${p}::${f}`)}>{title(p, f)}</button>)}</div>
      <div className="abcd-controls">
        <label>Question type<select value={group.key} onChange={e => setGroupKey(e.target.value)}>{data.groups.map(g => <option key={g.key} value={g.key}>{g.family ? "↳ " : ""}{title(g.pack, g.family)} · {g.cases}</option>)}</select></label>
        <label>Model<select value={model} onChange={e => setModel(e.target.value)}><option value="">Compare all {result.entrants.length} profiles</option>{result.entrants.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}</select></label>
        <label>Question set<select value={activeScope} onChange={e => setScope(e.target.value)} disabled={!group.reference_n}><option value="shared" disabled={noSharedQuestions}>Same supported questions for all models{noSharedQuestions ? " · none for this type" : ""}</option><option value="supported">Each model's attempted questions</option>{!group.reference_n && <option value="teacher">AI-teacher agreement only</option>}</select></label>
        <label>Score<select value={metric} onChange={e => setMetric(e.target.value)}><option value="label">Selected answer</option><option value="strict">Correct + usable output</option></select></label>
      </div>
      <div className="analysis-scope"><div className="scope-heading"><h3>{title(group.pack, group.family)}</h3>{leadScore != null && <div className="leading-score"><strong>{percent(leadScore)}</strong><span>{lead.name}{!model ? " · highest displayed score" : ""}</span></div>}</div><p>{activeScope === "teacher" ? `${group.teacher_n} AI-teacher questions. Agreement with AI answers, not independent accuracy.` : activeScope === "shared" ? `${group.shared_n.toLocaleString()} identical answer-key questions per model. ${group.reference_n - group.shared_n} excluded for common support/completion.` : `${group.reference_n.toLocaleString()} planned answer-key questions. Supported denominators can differ; capacity failures in the historical record remain failures.`} {group.teacher_n > 0 && activeScope !== "teacher" ? `${group.teacher_n} AI-teacher cases excluded.` : ""}</p>
        <button className="text-button" onClick={() => onCases({ pack: group.pack, family: group.family, model })}>Open these questions →</button></div>
      {noSharedQuestions && <p className="score-note">No questions of this type were supported by every model. Showing each model’s attempted questions automatically, with unsupported and missing counts alongside.</p>}
      {result.run_id === findings.run_id && group.family === "BANKING77" && <p className="slice-insight">This task supplies all 77 intents. Plumb and the tested SemIf interface accept 16. Winnow’s native server accepts 64, but Arena initially declared 255: all 500 requests were rejected. Its historical 0/500 below records that capacity mismatch and does not measure banking decision quality. These cases are outside the shared headline for every model.</p>}
      {result.run_id === findings.run_id && group.family === "AG News" && <p className="slice-insight">English Laya matches 34 labels that Jev misses; Jev matches 14 that Laya misses. Both match 427; both miss 25. These are answer-key matches: inspect case <button className="text-button" onClick={() => onCases({pack:group.pack,family:group.family,search:"classification-ag news-450"})}>450’s basketball / World reference →</button></p>}
      {result.run_id === findings.run_id && group.family === "SciFact" && <div className="slice-insight"><h3>Which relevant documents were found?</h3><p>453 irrelevant documents; 47 relevant. The first-option control scores 90.6% while finding none of the 47.</p><div className="table-scroll"><table className="task-ranking"><thead><tr><th>Model</th><th>Relevant found / 47</th><th>Irrelevant passed through</th><th>Precision of “yes”</th></tr></thead><tbody>{Object.entries(findings.relevance).filter(([id])=>model ? id===model : ["jev","winnow","decider","laya","uniform"].includes(id)).map(([id,r])=><tr key={id}><td>{result.entrants.find(e=>e.id===id)?.name || id}</td><td>{r.positive.correct} / {r.positive.n}</td><td>{r.confusion.find(c=>c.gold==="no"&&c.selected==="yes")?.n || 0}</td><td>{percent(r.positive_precision)}</td></tr>)}</tbody></table></div><p className="small muted">Selected-label diagnostics, independent of the output-validity selector below. Precision is undefined when a model never selects “yes.”</p></div>}
      <div className="table-scroll"><table className="task-ranking"><thead><tr><th>Model</th><th>{activeScope === "teacher" ? "Agreement" : "Accuracy"}</th><th>{activeScope === "teacher" ? "Matches / scored" : "Correct / scored"}</th><th>{activeScope === "teacher" ? "Non-matches" : "Not correct"}</th><th>Failed output or request</th><th>Coverage · entire question type</th><th>Quality P50 / P95</th><th>Evidence</th></tr></thead><tbody>{rows.map((e, i) => {
        const c = e.counts!, value = c[`${metric}_accuracy` as keyof Counts] as number | null;
        const coverage = group.models[e.id][activeScope === "teacher" ? "teacher" : "supported"];
        const correct = metric === "label" ? c.label_correct : c.strict_correct;
        const unavailable = coverage.unsupported === coverage.planned && coverage.planned > 0 ? "Unsupported" : coverage.missing === coverage.planned && coverage.planned > 0 ? "Not run" : "No scored questions";
        return <tr key={e.id} className={i === 0 && value != null && !model ? "leading-row" : ""}><td>{e.name}</td><td><strong>{value == null ? unavailable : percent(value)}</strong>{value != null && <span className="table-bar"><i style={{ width: `${value * 100}%` }}/></span>}</td><td>{c.n ? `${correct.toLocaleString()} / ${c.n.toLocaleString()}` : "—"}</td><td>{c.n ? (c.n - correct).toLocaleString() : "—"}</td><td>{c.n ? <>{c.failed.toLocaleString()} <small>{c.invalid.toLocaleString()} invalid outputs included</small></> : "—"}</td><td>{coverage.n.toLocaleString()} / {coverage.planned.toLocaleString()} attempted<small>{coverage.unsupported.toLocaleString()} unsupported · {coverage.missing.toLocaleString()} missing</small></td><td>{time(c.p50_ms)} / {time(c.p95_ms)}</td><td><button className="text-button" onClick={() => onCases({ pack: group.pack, family: group.family, model: e.id })}>Inspect →</button></td></tr>;
      })}</tbody></table></div>
      <p className="small muted">{activeScope === "teacher" ? "Matches + non-matches" : "Correct + not correct"} equals the scored count. Unsupported means the input exceeded a tested model or interface limit; it does not mean a wrong answer. Missing means no saved prediction. Coverage counts the entire selected question type{activeScope !== "teacher" ? ", excluding AI-teacher cases" : ""}, even when the score uses only shared questions. Failed outputs or requests are a separate diagnostic on the scored questions; a selected answer can match the key while its output fails validation.</p>
      <p className="small muted">Sorted by the selected score; ties share the same measured result. Descriptive slices, not significance tests. Quality-request timing includes failed attempts and differs from the dedicated short-input timing blocks. Whole-run confidence and workflow diagnostics follow below.</p>
    </>}
  </section>;
}

export function EvidenceExplorer({ rid, result }: { rid: string | null; result: Result | null }) {
  const [filters, setFilters] = useViewState(`cases:${rid}:filters`, { pack: "", family: "", model: "", kind: "", outcome: "", search: "", offset: 0 });
  const [search, setSearch] = useViewState(`cases:${rid}:search`, ""), [index, setIndex] = useState<CaseIndex | null>(null);
  const [chosen, setChosen] = useViewState(`cases:${rid}:chosen`, ""), [detail, setDetail] = useState<{ case: Case; predictions: Prediction[] } | null>(null);
  const [error, setError] = useState(""), [loading, setLoading] = useState(false), [reveal, setReveal] = useState(false);
  const immutable = result?.status === "complete";
  const change = (patch: Partial<typeof filters>) => { setFilters(f => ({ ...f, ...patch, offset: 0 })); setChosen(""); setDetail(null); };
  useEffect(() => { const timer = setTimeout(() => setFilters(f => f.search === search ? f : { ...f, search, offset: 0 }), 250); return () => clearTimeout(timer); }, [search]);
  useEffect(() => {
    if (!rid || window.__ARENA_REPORT__) return;
    const abort = new AbortController(); setLoading(true); setError(""); setDetail(null);
    const q = new URLSearchParams({ ...filters, offset: String(filters.offset), limit: "30", index_only: "true" });
    read<CaseIndex>(`/runs/${rid}/cases?${q}`, abort.signal, immutable).then(d => {
      if (abort.signal.aborted) return; setIndex(d); setChosen(old => d.cases.some(c => c.id === old) ? old : d.cases[0]?.id || ""); setLoading(false);
    }).catch(e => { if (!abort.signal.aborted) { setError(e.message); setLoading(false); } });
    return () => abort.abort();
  }, [rid, filters, immutable]);
  useEffect(() => {
    if (!rid || !chosen || loading || window.__ARENA_REPORT__) return;
    const abort = new AbortController(); setDetail(null); setReveal(false);
    read<{ case: Case; predictions: Prediction[] }>(`/runs/${rid}/cases/${encodeURIComponent(chosen)}${filters.model ? `?model=${encodeURIComponent(filters.model)}` : ""}`, abort.signal, immutable)
      .then(d => { if (!abort.signal.aborted) setDetail(d); }).catch(e => { if (!abort.signal.aborted) setError(e.message); });
    return () => abort.abort();
  }, [rid, chosen, filters.model, loading, immutable]);
  if (window.__ARENA_REPORT__) return <p>Exact case text stays in the local Arena workspace. This report contains aggregate evidence only.</p>;
  if (!rid) return <p>Choose a saved run to inspect its questions.</p>;
  const c = detail?.case, facets = index?.facets || [], packs = [...new Set(facets.map(f => f.pack))];
  return <><div className="explorer-controls abcd-controls">
    <label>Jump to question type<select value={`${filters.pack}::${filters.family}`} onChange={e => { const [pack, family] = e.target.value.split("::"); change({ pack, family }); }}><option value="::">All question types</option>{packs.map(p => <optgroup key={p} label={p}><option value={`${p}::`}>All {title(p, "")}</option>{facets.filter(f => f.pack === p).map(f => <option key={f.family} value={`${p}::${f.family}`}>{title(p, f.family)} · {f.count}</option>)}</optgroup>)}</select></label>
    <label>Model<select value={filters.model} onChange={e => change({ model: e.target.value, outcome: "" })}><option value="">All model responses</option>{result?.entrants.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}</select></label>
    <label>Outcome<select value={filters.outcome} disabled={!filters.model} onChange={e => change({ outcome: e.target.value })}><option value="">All outcomes</option><option value="correct">Selected answer matches</option><option value="wrong">Selected answer differs</option><option value="failed">Failed output or request</option><option value="unsupported">Unsupported</option></select></label>
    <label>Answer format<select value={filters.kind} onChange={e => change({ kind: e.target.value })}><option value="">All formats</option><option value="choice">Choice</option><option value="noul">Yes / no</option><option value="score">Ordinal score</option></select></label>
  </div>{error && <p role="alert">{error}</p>}<div className="case-workspace">
    <aside className="case-list"><div className="search"><input aria-label="Search all cases" placeholder="Search all cases or paste an ID…" value={search} onChange={e => setSearch(e.target.value)}/></div>
      <p className="small muted" role="status">{loading ? "Loading questions…" : `${(index?.total || 0).toLocaleString()} matching questions`}</p>
      <div className="case-list-items" aria-busy={loading}>{index?.cases.map(item => <button key={item.id} disabled={loading} className={chosen === item.id ? "selected" : ""} onClick={() => setChosen(item.id)}><span>{title(item.pack, item.family)}<small>{item.preview}</small><small>{item.id}</small></span></button>)}</div>
      <div className="pagination"><button disabled={loading || !filters.offset} onClick={() => setFilters(f => ({ ...f, offset: Math.max(0, f.offset - 30) }))}>Previous</button><span>{index?.total ? filters.offset + 1 : 0}–{Math.min(filters.offset + 30, index?.total || 0)} / {index?.total || 0}</span><button disabled={loading || filters.offset + 30 >= (index?.total || 0)} onClick={() => setFilters(f => ({ ...f, offset: f.offset + 30 }))}>Next</button></div>
      {!!index?.total && <label className="page-jump">Page<select aria-label="Jump to page" value={Math.floor(filters.offset / 30)} onChange={e => setFilters(f => ({ ...f, offset: Number(e.target.value) * 30 }))}>{Array.from({ length: Math.ceil(index.total / 30) }, (_, i) => <option key={i} value={i}>{i + 1}</option>)}</select></label>}
    </aside><section className="case-detail" aria-busy={loading || (!!chosen && !detail)}>{c ? <>
      <div className="eyebrow">{c.pack} / {c.id}</div><h2>{c.question.text}</h2><div className="case-tags"><span className="tag">{c.question.labels.length} choices</span><span className="tag">{c.label_status === "teacher" ? "AI-TEACHER ANSWER" : c.label_status === "formal" ? "RULE-DERIVED ANSWER" : "DATASET ANSWER KEY"}</span></div>
      <div className="evidence-block"><CaseState text={c.state}/></div>
      {c.question.rubric && <details className="explain"><summary>Decision rules supplied to the model</summary><p>{c.question.rubric}</p></details>}
      {c.question.labels.length <= 8 ? <div className="answer-options">{c.question.labels.map(l => <span key={l}>{l}</span>)}</div> : <details className="explain"><summary>Show all {c.question.labels.length} allowed answers</summary><div className="answer-options">{c.question.labels.map(l => <span key={l}>{l}</span>)}</div></details>}
      <button className="button secondary" onClick={() => setReveal(!reveal)}>{reveal ? "Hide answers" : "Reveal reference and model answers"}</button>
      {reveal && <div className="answer-reveal"><div className="reference"><span>Saved reference</span><strong>{c.gold}</strong>{!!c.acceptable?.length && <small>Also accepted: {c.acceptable.join(", ")}</small>}</div><h3>Model decisions</h3><div className="decision-rows">{detail.predictions.map(p => <div key={p.model_id}><div className="decision-title"><strong>{result?.entrants.find(e => e.id === p.model_id)?.name || p.model_id}</strong><span className={[c.gold, ...(c.acceptable || [])].includes(p.selected || "") ? "accent" : "muted"}>{p.selected || "No selected answer"}</span><small>{time(p.request_ms)} · {p.status}</small></div>{p.error && <p className="small muted">{p.error}</p>}{p.probabilities && <details className="explain"><summary>Option probabilities · {p.probability_source}</summary><div className="prob-bars">{Object.entries(p.probabilities).map(([name, v]) => <div key={name}><span>{name}</span><div><i style={{ width: `${Math.max(0, Math.min(1, v)) * 100}%` }}/></div><b>{percent(v)}</b></div>)}</div></details>}</div>)}</div>
      {result?.judge_jobs.filter(j => j.data.item.case_id === c.id && j.data.grade).map(j => <details className="explain" key={j.job_id}><summary>Separate Astra audit · {j.data.grade?.verdict}</summary><p>{j.data.grade?.rationale}</p></details>)}</div>}
    </> : <p role="status">{loading || chosen ? "Loading saved question…" : "No matching questions. Change the filters or search."}</p>}</section>
  </div></>;
}
