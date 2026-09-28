import React, { useEffect, useMemo, useState, useCallback } from "react";

import { createRoot } from "react-dom/client";

import {
  Activity,
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Circle,
  Command,
  Cpu,
  Database,
  ExternalLink,
  FlaskConical,
  Layers3,
  Pause,
  Play,
  RotateCcw,
  Search,
  Settings2,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Square,
  Terminal,
  Timer,
  TriangleAlert,
  X,
  Zap,
} from "lucide-react";

import type {
  Model,
  Ready,
  Run,
  Result,
  Metrics,
  Case,
  Prediction,
  ArenaEvent,
} from "./types";


import "./styles.css";
import { AppShell } from "../../shared/AppShell";

import { Operations, EpisodeReplay } from "./Operations";
import { Takeaways, ModelGuide, SourcesGuide, CaseState, TaskBreakdown, ABCDResults } from "./Guide";
import { ABCDCases } from "./ABCDCases";

const terminal = [
  "complete",
  "failed",
  "cancelled",
  "partial",
  "judging_incomplete",
  "interrupted",
];

const stages = [
  "preflight",
  "loading",
  "warming",
  "evaluating",
  "performance",
  "episodes",
  "unloading",
  "judging",
  "verifying",
  "complete",
];

declare global {
  interface Window {
    __ARENA_REPORT__?: { run: Run; result: Result; readiness: Ready };
  }
}

const offline = window.__ARENA_REPORT__;

let token = "";

async function api<T>(path: string, body?: unknown): Promise<T> {
  if (offline) {
    if (body !== undefined)
      throw new Error(
        "This saved report is read-only. Launch Jev Arena to run models.",
      );
    return (
      path === "/readiness"
        ? offline.readiness
        : path === "/runs"
          ? [offline.run]
          : path.endsWith("/results")
            ? offline.result
            : path.includes("/cases")
              ? { total: 0, cases: [], predictions: [] }
              : path.endsWith("/timeline")
                ? []
                : offline.run
    ) as T;
  }

  if (body !== undefined && !token)
    token = (await (await fetch("/api/session")).json()).token;

  const r = await fetch(
    "/api" + path,
    body === undefined
      ? undefined
      : {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Arena-Token": token,
          },
          body: JSON.stringify(body),
        },
  );

  if (!r.ok) {
    const data = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : JSON.stringify(data.detail),
    );
  }
  return r.json();
}

const pct = (v: number | null | undefined, d = 1) =>
  v == null ? "—" : `${(v * 100).toFixed(d)}%`;

const num = (v: number | null | undefined, d = 0) =>
  v == null ? "—" : v.toLocaleString(undefined, { maximumFractionDigits: d });

const ms = (v: number | null | undefined) =>
  v == null
    ? "—"
    : v >= 1000
      ? `${(v / 1000).toFixed(2)}s`
      : v < 1
        ? "<1ms"
        : `${v.toFixed(v < 10 ? 1 : 0)}ms`;

const label = (s: string) =>
  s.replaceAll("_", " ").replace(/^./, (x) => x.toUpperCase());

const answerScore = (e: Result["entrants"][number]) => e.matched?.selected_label_accuracy ?? null;
const typicalTime = (result: Result | null, id: string) => {
  const blocks = result?.performance?.[id]?.blocks.map(b=>b.p50_ms).sort((a,b)=>a-b) || [];
  return blocks.length ? blocks[Math.floor(blocks.length/2)] : result?.entrants.find(e=>e.id===id)?.metrics.p50_ms;
};
function App() {
  const [page, setPage] = useState("arena"),
    [caseDataset, setCaseDataset] = useState("arena"),
    [ready, setReady] = useState<Ready | null>(null),
    [runs, setRuns] = useState<Run[]>([]),
    [rid, setRid] = useState<string | null>(null),
    [result, setResult] = useState<Result | null>(null),
    [events, setEvents] = useState<ArenaEvent[]>([]);

  const [selected, setSelected] = useState<string[]>([
      "jev",
      "plumb",
      "decider",
      "winnow",
      "semif",
      "clm",
      "nimble",
      "laya",
    ]),
    [preset, setPreset] = useState("full"),
    [judge, setJudge] = useState(true),
    [drawer, setDrawer] = useState(false),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [focus, setFocus] = useState<string | null>(null),
    [present, setPresent] = useState(false);

  useEffect(() => { window.scrollTo({top:0, behavior:"instant"}); }, [page]);

  const refresh = useCallback(async () => {
    try {
      const [a, b] = await Promise.all([
        api<Ready>("/readiness"),
        api<Run[]>("/runs"),
      ]);
      setReady(a);
      setRuns(b);
      setRid(
        (old) =>
          old ||
          b.find((r) => !terminal.includes(r.status))?.id ||
          b.find(
            (r) => r.status === "complete" && r.request.model_ids.length > 1,
          )?.id ||
          b.find((r) => r.status === "complete")?.id ||
          b[0]?.id ||
          null,
      );
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 12000);
    return () => clearInterval(t);
  }, [refresh]);

  const loadResult = useCallback(async () => {
    if (rid) {
      try {
        setResult(await api<Result>(`/runs/${rid}/results`));
      } catch (e) {
        setError((e as Error).message);
      }
    }
  }, [rid]);

  useEffect(() => {
    setResult(null);
    setEvents([]);
    loadResult();
    if (!rid || offline) return;
    let update: ReturnType<typeof setTimeout> | null = null;
    const es = new EventSource(`/api/runs/${rid}/events`);
    es.addEventListener("arena", (e) => {
      const item = JSON.parse((e as MessageEvent).data);
      setEvents((prev) => [...prev.slice(-500), item]);
      if (!update)
        update = setTimeout(() => {
          loadResult();
          refresh();
          update = null;
        }, 1000);
    });
    es.addEventListener("done", () => {
      es.close();
      loadResult();
      refresh();
    });
    return () => {
      es.close();
      if (update) clearTimeout(update);
    };
  }, [rid, loadResult, refresh]);

  useEffect(() => {
    if (!drawer) return;
    const before = document.activeElement as HTMLElement | null;
    const dialog = document.querySelector(".drawer") as HTMLElement;
    const focusable = () =>
      Array.from(
        dialog.querySelectorAll<HTMLElement>(
          "button:not([disabled]),input,select,a[href]",
        ),
      );
    focusable()[0]?.focus();
    const key = (e: KeyboardEvent) => {
      if (e.key === "Escape") setDrawer(false);
      if (e.key === "Tab") {
        const all = focusable(),
          first = all[0],
          last = all.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", key);
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", key);
      document.body.style.overflow = previous;
      before?.focus();
    };
  }, [drawer]);

  const current = runs.find((r) => r.id === rid),
    active = !!current && !terminal.includes(current.status),
    models = ready?.models || [],
    blocked = models.filter((m) => selected.includes(m.id) && !m.ready),
    metricRows = result?.entrants || [];

  const displayPreset =
    active || offline ? current?.request.preset || preset : preset;

  const planned = result
    ? result.case_count * result.entrants.length
    : (preset === "full" ? 7671 : preset === "demo" ? 120 : 36) *
      selected.length;

  const completed = metricRows.reduce((sum, e) => sum + e.metrics.completed, 0),
    best = metricRows
      .filter((e) => answerScore(e) != null)
      .sort((a, b) => answerScore(b)! - answerScore(a)!)[0];

  const runStages = stages.filter(
    (s) =>
      !(
        (s === "performance" && current?.request.preset !== "full") ||
        (s === "episodes" &&
          !["full", "demo"].includes(current?.request.preset || "")) ||
        (s === "judging" && !current?.request.judge)
      ),
  );

  const stage =
    (events.filter((e) => e.kind === "stage").at(-1)?.data.stage as string) ||
    current?.status ||
    "ready";

  const liveModel = events.filter((e) => e.kind === "model").at(-1)?.data
    .model_id as string | undefined;

  async function start() {
    setBusy(true);
    setError("");
    try {
      const r = await api<{ id: string }>("/runs", {
        preset,
        model_ids: selected,
        judge,
        paid_cap_usd: 5,
        seed: 5090,
        idempotency_key: crypto.randomUUID(),
      });
      setRid(r.id);
      setPage("arena");
      setDrawer(false);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
      setDrawer(true);
    } finally {
      setBusy(false);
    }
  }

  async function mutate(path: string) {
    try {
      await api(path, {});
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  function toggle(mid: string) {
    setSelected((s) =>
      s.includes(mid) ? s.filter((x) => x !== mid) : [...s, mid],
    );
  }

  return (
    <>
      <AppShell
        appName="Jev Arena"
        description="Decision model lab"
        navigation={[
          { id: "arena", label: "Overview", icon: Activity },
          { id: "takeaways", label: "What we learned", icon: Sparkles },
          { id: "models", label: "Model guide", icon: Cpu },
          { id: "abcd", label: "Support conversations", icon: Database },
          { id: "sources", label: "Tests & scoring", icon: ShieldCheck },
          { id: "results", label: "Results", icon: Layers3 },
          { id: "cases", label: "Case explorer", icon: FlaskConical },
          { id: "replay", label: "Workflow replays", icon: Play },
          { id: "run", label: "Run a new test", icon: Play },
          { id: "setup", label: "Setup", icon: Settings2 },
        ]}
        activePage={page}
        onNavigate={setPage}
        presenter={present}
        onPresenterChange={setPresent}
        status={offline ? "Saved report" : ready?.hardware.gpu?.name.replace("NVIDIA GeForce ", "") || "Local workspace"}
        sidebarFooter={<><p>Saved evidence. Clear comparisons.</p><button className="text-button" onClick={()=>setPage("sources")}>All benchmark sources →</button></>}
        footerNote={page === "abcd" || (page === "cases" && caseDataset === "abcd") ? "abcd-test-v1 · Separate completed assessment" : result ? `${result.run_id} · ${label(current?.status || "")}` : "No synthetic measurements"}
        className={`page-${page}`}
      >
          {offline && (
            <div className="setup-progress">
              <ShieldCheck size={17} /> Saved report · read-only · all charts
              and replays use the exported measurements.
            </div>
          )}

          {error && (
            <div className="alert" role="alert">
              <TriangleAlert size={17} />
              <span>{error}</span>
              <button onClick={() => setError("")} aria-label="Dismiss error">
                <X size={16} />
              </button>
            </div>
          )}

          <div className="page-heading">
            <div>
              <div className="eyebrow">
                <span className="status-dot" />
                {active
                  ? "EVALUATION IN PROGRESS"
                  : completed
                    ? "MEASURED RESULTS"
                    : "DECISION MODEL LAB"}
              </div>
              <h1>
                {page === "models" ? "Meet the models." : page === "takeaways" ? "What we learned." : page === "sources" ? "Tests & scoring." : page === "abcd" ? "Support conversations." : page === "run" ? "Run a new test." : page === "chart" ? "Accuracy and speed." : page === "arena"
                  ? "Measured results."
                  : page === "results"
                    ? "Results, in detail."
                    : page === "cases"
                      ? "Every decision."
                      : page === "replay"
                        ? "Run it back."
                        : "Ready your arena."}
              </h1>
              <p>
                {page === "models" ? "What each model is, what it needs, and where it fits." : page === "takeaways" ? "Practical lessons for software, automation and real-time decisions." : page === "sources" ? "Where the questions and answers come from." : page === "abcd" ? "A separate five-model assessment of support decisions with longer inputs." : page === "run" ? "New tests are saved separately. Existing results remain available." : page === "chart" ? "Higher is more accurate. Left is faster. Click a point to inspect it." : page === "arena"
                  ? "One headline comparison: the same answer-key questions for every model."
                  : page === "results"
                    ? "Compare quality, speed, coverage and confidence on identical cases."
                    : page === "cases"
                      ? "Trace a score back to its evidence, answer and reference."
                      : page === "replay"
                        ? "Two small workflow demonstrations, with saved scenarios and outcomes. Playback makes no model calls."
                        : "Prepare models, verify the judge and freeze the evaluation suite."}
              </p>
            </div>
            <div className="heading-actions">
              {runs.length > 0 && !(page === "cases" && caseDataset === "abcd") && page !== "abcd" && (
                <select
                  aria-label="Select saved run"
                  value={rid || ""}
                  onChange={(e) => setRid(e.target.value)}
                >
                  {runs.map((r) => (
                    <option value={r.id} key={r.id}>
                      {new Date(r.created * 1000).toLocaleDateString(
                        undefined,
                        { month: "short", day: "numeric" },
                      )}{" "}
                      · {r.request.preset} · {r.request.model_ids.length} models
                      · {r.id.slice(-6)} · {label(r.status)}
                    </option>
                  ))}
                </select>
              )}
              {rid && !offline && !(page === "cases" && caseDataset === "abcd") && page !== "abcd" && (
                <a
                  className="button secondary compact"
                  href={`/api/runs/${rid}/export`}
                >
                  <ArrowDownToLine size={16} /> Export
                </a>
              )}
              {(page === "run" || page === "setup") && (<button
                className="button secondary compact"
                disabled={!!offline}
                onClick={() => setDrawer(true)}
              >
                <SlidersHorizontal size={16} /> New test settings
              </button>)}

            </div>
          </div>

          {result?.run_id === "20260927-205440-6350b9" && (page === "arena" || page === "results") && (
            <details className="explain"><summary>How to read the headline: 4,635 identical questions per model</summary>
              <p>Answer accuracy counts selected answers that match the answer key. It ignores probability-format checks, which remain in the detailed results. This presents the existing shared-question comparison; it does not change saved scoring.</p>
              <p>We exclude 1,000 questions with more options than some models accept, plus 36 inputs exceeding a tested context setting. The same exclusions apply to every model. These 4,635 questions are a restricted comparison, not all 7,671 cases.</p>
              <p>Winnow accepts up to 64 choices. Arena mistakenly sent 500 banking questions with 77 choices. Those requests are outside this shared score. They remain in the original attempt log, not treated as reasoning errors here. The old 84.87% is a different, all-attempt strict score.</p>
            </details>
          )}
          {page === "models" && <ModelGuide selected={focus} onSelect={setFocus}/>}
          {page === "takeaways" && <><Takeaways onModels={()=>setPage("models")} onAbcd={()=>setPage("abcd")}/><TaskBreakdown/><p className="small muted">This findings page describes completed v2 (27 September) and ABCD (28 September), regardless of the saved run selected above.</p></>}
          {page === "sources" && <SourcesGuide/>}
          {page === "abcd" && <><button className="text-button" onClick={()=>{setCaseDataset("abcd");setPage("cases")}}>Inspect ABCD cases →</button><ABCDResults/></>}
          {page === "chart" && <section className="frontier-panel chart-large"><button className="text-button" onClick={()=>setPage("arena")}>← Back to overview</button><Frontier rows={metricRows} result={result} focus={focus} onFocus={setFocus}/><p className="small muted">Answer accuracy on shared questions. Typical time is the middle of three repeated timing-block medians; CLM supports only 172 of 200 timing inputs. Hosted timing includes network travel. One request at a time.</p></section>}

          {page === "arena" && (
            <>
              <div className="workspace-bar">
                <div className="workspace-tabs">
                  <button className="selected">Overview</button>
                  <button onClick={() => setPage("results")}>
                    Quality & confidence
                  </button>
                  <button onClick={() => setPage("replay")}>
                    Replay <ArrowUpRight size={12} />
                  </button>
                </div>
                <span className="scope-label">
                  {result
                    ? `${result.preset.toUpperCase()} · ${String(current?.manifest.version || "arena-v1").replace("arena-", "").toUpperCase()} · ${num(result.case_count)} CASES`
                    : "FULL ARENA · 7,671 CASES"}
                </span>
              </div>

              <div className="arena-layout">
                <div className="main-column">
                  <div className="metrics-strip">
                    <Metric
                      name="Decisions evaluated"
                      value={num(completed)}
                      detail={`of ${num(planned)} planned`}
                      large
                    />
                    <Metric
                      name="Best answer accuracy"
                      value={best ? pct(answerScore(best),2) : "—"}
                      detail={
                        best
                          ? `${best.name} · shared questions`
                          : "Awaiting measured results"
                      }
                    />
                    <Metric
                      name="Models in comparison"
                      value={String(
                        result?.entrants.length || selected.length,
                      ).padStart(2, "0")}
                      detail={
                        result
                          ? "Same frozen case manifest"
                          : "Main roster + optional controls"
                      }
                    />
                    <Metric
                      name="Main score"
                      value="Answer key"
                      detail={
                        (current ? current.request.judge : judge)
                          ? "Astra separately spot-checks a sample"
                          : "Scored against saved answers"
                      }
                      text
                    />
                  </div>

                  <section className="frontier-panel">
                    <div className="section-title">
                      <div>
                        <h2>Accuracy and speed</h2>
                        <p>
                          Higher is more accurate. Left is faster. Same shared-question score as the table.
                        </p>
                      </div>
                      <span className={`tag ${completed ? "measured" : ""}`}>
                        {completed
                          ? active
                            ? "LIVE MEASUREMENTS"
                            : "MEASURED"
                          : "AWAITING RUN"}
                      </span>
                    </div>
                    <Frontier
                      result={result}
                      rows={metricRows}
                      focus={focus}
                      onFocus={setFocus}
                    />
                    <div className="chart-foot">
                      <span>
                        <span className="tiny-square" /> Selected entrant
                      </span>
                      <span>
                        Repeated short-input timing · serial requests · network included for Jev
                      </span>
                      <button onClick={() => setPage("chart")}>
                        Enlarge chart <ArrowRight size={13} />
                      </button>
                    </div>
                  </section>

                  <section className="model-panel">
                    <div className="section-title">
                      <div>
                        <h2>
                          Entrant comparison{" "}
                          <span className="count">
                            {result?.entrants.length || selected.length}
                          </span>
                        </h2>
                      </div>
                      <button
                        className="text-button"
                        disabled={!!offline}
                        onClick={() => setDrawer(true)}
                      >
                        Manage entrants <SlidersHorizontal size={13} />
                      </button>
                    </div>
                    <p className="small muted score-note">One score: selected-answer accuracy on the same {num(metricRows[0]?.matched?.verified_count)} reference questions. Output checks and full attempt logs are in Results. Click a model for its profile.</p>
                    <div className="table-scroll"><table><thead><tr><th>MODEL</th><th>ANSWER ACCURACY</th><th>TYPICAL RESPONSE</th><th>OUTPUTS PASSING CHECKS</th></tr></thead><tbody>
                    {[...metricRows].sort((a,b)=>(answerScore(b)??-1)-(answerScore(a)??-1)).map(e=><tr key={e.id}>
                    <td><button className="model-link" onClick={()=>{setFocus(e.id);setPage("models")}}>{e.name} <ChevronRight size={14}/></button></td>
                    <td className="tabular bright">{pct(answerScore(e),2)}<small className="table-note">{num(e.matched?.selected_label_correct)} / {num(e.matched?.verified_count)} answers</small></td>
                    <td className="tabular">{ms(typicalTime(result,e.id))}</td>
                    <td>{pct(e.metrics.coverage, 2)}<small className="table-note">{num(e.metrics.valid)} / {num(e.metrics.planned)} planned · not accuracy</small></td>
                    </tr>)}</tbody></table></div>

                  </section>
                </div>


              </div>
              {result?.run_id === "20260927-205440-6350b9" && <Takeaways onModels={()=>setPage("models")} onAbcd={()=>setPage("abcd")}/>}

              <div className="method-strip">
                <div>
                  <ShieldCheck size={19} />
                  <span>
                    Evidence first
                    <strong>
                      Every result has a saved input, output and manifest.
                    </strong>
                  </span>
                </div>
                <div>
                  <Layers3 size={19} />
                  <span>
                    One model at a time
                    <strong>
                      Sequential GPU runs. Explicit capability limits.
                    </strong>
                  </span>
                </div>
                <button className="text-button" onClick={()=>setPage("sources")}>All benchmark sources <ExternalLink size={13}/></button>
              </div>
            </>
          )}

          {page === "results" && (
            <Results result={result} focus={focus} onFocus={setFocus} onProfile={(id)=>{setFocus(id);setPage("models")}} />
          )}

          {page === "cases" && (
            <><label className="case-dataset">Assessment<select value={caseDataset} onChange={e=>setCaseDataset(e.target.value)}><option value="arena">Arena v2 · 13-profile benchmark</option><option value="abcd">ABCD · support conversations</option></select></label>{caseDataset==="abcd"?<ABCDCases offline={!!offline}/>:<Cases rid={rid} models={models} result={result} />}</>
          )}

          {page === "replay" &&
            (result ? (
              <EpisodeReplay result={result} />
            ) : (
              <Replay rid={rid} result={result} />
            ))}

          {page === "run" && (<aside className="run-panel">
                  <div className="run-panel-top">
                    <span className="eyebrow">RUN CONTROL</span>
                    <span className="run-number">
                      {current
                        ? "#" + current.id.slice(-6).toUpperCase()
                        : "# NEW RUN"}
                    </span>
                  </div>
                  <div className="run-orbit">
                    <svg viewBox="0 0 180 180">
                      <circle cx="90" cy="90" r="77" className="orbit-bg" />
                      <circle
                        cx="90"
                        cy="90"
                        r="77"
                        className="orbit-progress"
                        strokeDasharray={`${Math.min(1, completed / Math.max(1, planned)) * 484} 484`}
                      />
                      {Array.from({ length: 40 }, (_, i) => {
                        const a = (i / 40) * Math.PI * 2;
                        return (
                          <line
                            key={i}
                            x1={90 + 66 * Math.cos(a)}
                            y1={90 + 66 * Math.sin(a)}
                            x2={90 + 69 * Math.cos(a)}
                            y2={90 + 69 * Math.sin(a)}
                          />
                        );
                      })}
                    </svg>
                    <div>
                      {active ? (
                        <Activity size={31} />
                      ) : current?.status === "complete" ? (
                        <Check size={32} />
                      ) : (
                        <Command size={30} />
                      )}
                      <strong>
                        {active
                          ? `${Math.round((completed / Math.max(planned, 1)) * 100)}%`
                          : current?.status === "complete"
                            ? "Complete"
                            : "New test"}
                      </strong>
                      <span>{active ? label(stage) : "SAVED RUN STATUS"}</span>
                    </div>
                  </div>
                  <p className="run-description">
                    A new Full test can take hours and use paid API calls. It creates a separate saved run. Previous results remain available in the run selector.
                  </p>

                  {active ? (
                    <button
                      className="button stop"
                      onClick={() => mutate(`/runs/${rid}/cancel`)}
                    >
                      <Square size={15} /> Stop run
                    </button>
                  ) : (
                    <button
                      className="button primary impress"
                      onClick={() => setDrawer(true)}
                      disabled={!!offline || busy || !selected.length}
                    >
                      {busy ? (
                        <Activity className="spin" size={18} />
                      ) : (
                        <Zap size={18} />
                      )}{" "}
                      Configure new test <ArrowRight size={18} />
                    </button>
                  )}

                  <button
                    className="preset-line"
                    disabled={!!offline || active}
                    onClick={() => setDrawer(true)}
                  >
                    <span>
                      {!active && !offline ? "Next: " : ""}
                      {label(displayPreset)} suite
                    </span>
                    <span>
                      {num(
                        displayPreset === "full"
                          ? 7671
                          : displayPreset === "demo"
                            ? 120
                            : 36,
                      )}{" "}
                      cases <ChevronDown size={12} />
                    </span>
                  </button>

                  {blocked.length > 0 && !active && (
                    <button
                      className="setup-hint"
                      onClick={() => {
                        setPage("setup");
                        setDrawer(false);
                      }}
                    >
                      <TriangleAlert size={14} />
                      <span>{blocked.length} selected entrants need setup</span>
                      <ArrowUpRight size={13} />
                    </button>
                  )}

                  <div className="stage-list">
                    {runStages.map((s, i) => {
                      const at = runStages.indexOf(stage),
                        done = current?.status === "complete" || at > i;
                      return (
                        <div
                          key={s}
                          className={`${done ? "done" : ""} ${stage === s ? "current" : ""}`}
                        >
                          <span>
                            {done ? (
                              <Check size={11} />
                            ) : (
                              String(i + 1).padStart(2, "0")
                            )}
                          </span>
                          <b>{label(s)}</b>
                          {stage === s && active && (
                            <span className="stage-live" />
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <div className="hardware-mini">
                    <Cpu size={17} />
                    <div>
                      <strong>
                        {ready?.hardware.gpu?.name.replace(
                          "NVIDIA GeForce ",
                          "",
                        ) || "GPU not detected"}
                      </strong>
                      <span>
                        {num(
                          (ready?.hardware.gpu?.memory_total_mb || 0) / 1024,
                          1,
                        )}{" "}
                        GB VRAM · {num(ready?.hardware.gpu?.temperature_c)}°C
                      </span>
                    </div>
                    <span className="status-dot" />
                  </div>
                  {liveModel && active && (
                    <div className="currently">
                      Now running{" "}
                      <strong>
                        {models.find((m) => m.id === liveModel)?.name}
                      </strong>
                    </div>
                  )}

                  {current?.error && (
                    <div className="run-error">
                      {current.error}
                      {!active && current.status !== "complete" && (
                        <button
                          className="text-button"
                          onClick={() => mutate(`/runs/${rid}/resume`)}
                        >
                          Resume saved run <RotateCcw size={13} />
                        </button>
                      )}
                    </div>
                  )}
                </aside>)}

          {page === "setup" && (
            <Setup
              ready={ready}
              selected={selected}
              toggle={toggle}
              onRefresh={refresh}
              onError={setError}
              onLocal={() => {
                setSelected(
                  models
                    .filter((m) => m.ready && !m.hosted && m.id !== "uniform")
                    .map((m) => m.id),
                );
                setPreset("smoke");
                setDrawer(true);
              }}
            />
          )}

      </AppShell>

      {drawer && (
        <div className="drawer-backdrop" onClick={() => setDrawer(false)}>
          <section
            className="drawer"
            role="dialog"
            aria-modal="true"
            aria-label="Configure evaluation"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="drawer-title">
              <div>
                <span className="eyebrow">NEXT EVALUATION</span>
                <h2>Configure your run.</h2>
              </div>
              <button
                className="icon-btn"
                onClick={() => setDrawer(false)}
                aria-label="Close configuration"
              >
                <X />
              </button>
            </div>
            <label className="field-label">Evaluation suite</label>
            <div className="preset-options">
              {[
                ["smoke", "36", "Verify the setup"],
                ["demo", "120", "A short live comparison"],
                ["full", "7,671", "The current frozen Arena suite"],
              ].map(([p, n, desc]) => (
                <button
                  className={preset === p ? "selected" : ""}
                  key={p}
                  onClick={() => setPreset(p)}
                >
                  <span>
                    {label(p)} <b>{n}</b>
                  </span>
                  <small>{desc}</small>
                </button>
              ))}
            </div>
            <div className="field-row">
              <label className="field-label">
                Entrants <span>{selected.length} selected</span>
              </label>
              <button
                className="text-button"
                onClick={() =>
                  setSelected(
                    models
                      .filter((m) => m.ready && m.id !== "uniform")
                      .map((m) => m.id),
                  )
                }
              >
                Select ready
              </button>
            </div>
            <div className="entrant-select">
              {models.map((m) => (
                <label key={m.id}>
                  <input
                    type="checkbox"
                    checked={selected.includes(m.id)}
                    onChange={() => toggle(m.id)}
                  />
                  <span>
                    <strong>{m.name}</strong>
                    <small>
                      {m.hosted ? "Hosted" : m.size + " · Local"}
                      {m.diagnostic ? " · Control" : ""}
                    </small>
                  </span>
                  <span className={m.ready ? "accent" : "muted"}>
                    {m.ready ? "Ready" : "Setup"}
                  </span>
                </label>
              ))}
            </div>
            <label className="judge-toggle">
              <input
                type="checkbox"
                checked={judge}
                onChange={(e) => setJudge(e.target.checked)}
              />
              <span>
                <strong>Optional Astra answer-key spot-check</strong>
                <small>Separate from accuracy; uses Codex CLI usage.</small>
              </span>
            </label>
            <div className="config-note">
              <ShieldCheck size={16} />
              <span>
                This starts a separate test with a new $5 run cap. Full can take hours. Earlier results stay saved; this is not replay. Check any project-wide spending limits before starting.
              </span>
            </div>
            <button
              className="button primary"
              disabled={busy || !selected.length || active}
              onClick={start}
            >
              <Zap size={17} /> Start new {label(preset)} test{" "}
              <ArrowRight size={17} />
            </button>
            {blocked.length > 0 && (
              <p className="muted small">
                {blocked.length} selected entrants need preparation. Open Setup
                to resolve them.
              </p>
            )}
          </section>
        </div>
      )}
    </>
  );
}

function Metric({
  name,
  value,
  detail,
  large = false,
  text = false,
}: {
  name: string;
  value: string;
  detail: string;
  large?: boolean;
  text?: boolean;
}) {
  return (
    <div
      className={`metric ${large ? "major" : ""} ${text ? "text-metric" : ""}`}
    >
      <span>{name}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </div>
  );
}

function Frontier({
  result,
  rows,
  focus,
  onFocus,
}: {
  result: Result | null;
  rows: Result["entrants"];
  focus: string | null;
  onFocus: (id: string | null) => void;
}) {
  const chartRows = rows.map(e=>({...e, metrics:{...e.metrics, accuracy:answerScore(e), p50_ms:typicalTime(result,e.id)??null}}));
  const measured = chartRows.filter(
      (e) => e.metrics.p50_ms != null && e.metrics.accuracy != null,
    ),
    max = Math.max(100, ...measured.map((e) => e.metrics.p50_ms! * 1.5));

  const x = (v: number) =>
      72 + (Math.log10(Math.max(1, v)) / Math.log10(max)) * 740,
    y = (v: number) => 375 - v * 302;

  return (
    <div className="frontier-chart">
      <svg
        viewBox="0 0 880 430"
        role="img"
        aria-label={
          measured.length
            ? "Accuracy versus median request latency"
            : "Empty quality versus latency chart, awaiting measured results"
        }
      >
        <defs>
          <pattern
            id="dots"
            width="18"
            height="18"
            patternUnits="userSpaceOnUse"
          >
            <circle cx="1" cy="1" r=".65" fill="var(--line)" />
          </pattern>
        </defs>
        <rect x="72" y="38" width="740" height="338" fill="url(#dots)" />
        {[0, 0.25, 0.5, 0.75, 1].map((v) => (
          <g key={v}>
            <line x1="72" x2="812" y1={y(v)} y2={y(v)} className="grid-line" />
            <text x="53" y={y(v) + 4} textAnchor="end">
              {v * 100}%
            </text>
          </g>
        ))}
        {[1, 10, 100, 1000, 10000]
          .filter((v) => v <= max)
          .map((v) => (
            <g key={v}>
              <line
                x1={x(v)}
                x2={x(v)}
                y1="38"
                y2="375"
                className="grid-line vertical-line"
              />
              <text x={x(v)} y="397" textAnchor="middle">
                {ms(v)}
              </text>
            </g>
          ))}
        <text x="73" y="22" className="axis-label">
          ANSWER ACCURACY · SAME QUESTIONS ↑
        </text>
        <text x="812" y="420" textAnchor="end" className="axis-label">
          TYPICAL RESPONSE TIME · LOG SCALE →
        </text>
        <text x="91" y="62" className="ideal-label">
          HIGH QUALITY · LOW LATENCY
        </text>
        {measured.map((e, i) => {
          const chosen = focus === e.id || (!focus && i === 0);
          return (
            <g
              key={e.id}
              className={`chart-point ${chosen ? "selected" : ""}`}
              tabIndex={0}
              role="button"
              aria-label={`${e.name}: ${pct(e.metrics.accuracy)}, ${ms(e.metrics.p50_ms)}`}
              onMouseEnter={() => onFocus(e.id)}
              onFocus={() => onFocus(e.id)}
              onClick={() => onFocus(e.id)}
              onKeyDown={(ev) => {
                if (ev.key === "Enter") onFocus(e.id);
              }}
            >
              <circle
                className="point-halo"
                cx={x(e.metrics.p50_ms!)}
                cy={y(e.metrics.accuracy!)}
                r={chosen ? 15 : 10}
              />
              <circle
                cx={x(e.metrics.p50_ms!)}
                cy={y(e.metrics.accuracy!)}
                r={chosen ? 5.5 : 4}
              />
              {chosen && (
                <text
                  x={Math.min(740, x(e.metrics.p50_ms!) + 13)}
                  y={y(e.metrics.accuracy!) - 12}
                >
                  {e.name}
                </text>
              )}
            </g>
          );
        })}
        {!measured.length && (
          <g className="chart-empty">
            <path d="M408 142h20l9-19 13 42 12-30h25" />
            <text x="447" y="199" textAnchor="middle">
              Your first run starts the comparison.
            </text>
            <text x="447" y="218" textAnchor="middle" className="sub">
              Configure a new test to collect measurements.
            </text>
          </g>
        )}
      </svg>
    </div>
  );
}

function Results({
  onProfile,
  result,
  focus,
  onFocus,
}: {
  result: Result | null;
  onProfile: (id: string) => void;
  focus: string | null;
  onFocus: (s: string) => void;
}) {
  if (!result || !result.entrants.length)
    return (
      <Empty
        icon={Layers3}
        title="No measured results yet"
        detail="Run a comparison or choose a saved evaluation to inspect the results."
      />
    );

  const e = result.entrants.find((e) => e.id === focus) || result.entrants[0],
    m = e.metrics;

  const reviews = result.judge_jobs.filter(
    (j) => j.status === "complete" && j.data.models.includes(e.id),
  );

  return (
    <>
      <div className="results-select">
        {result.entrants.map((r) => (
          <button
            className={r.id === e.id ? "selected" : ""}
            key={r.id}
            onClick={() => onFocus(r.id)}
          >
            {r.name}
            <span>{pct(answerScore(r),2)}</span>
          </button>
        ))}
      </div>
      <div className="results-context">
        <h2>{e.name}</h2><button className="text-button" onClick={()=>onProfile(e.id)}>About this model →</button>
        <span>
          {num(e.matched.selected_label_correct)} / {num(e.matched.verified_count)} shared answer-key questions correct · AI-teacher answers excluded
        </span>
      </div>
      <div className="metrics-strip result-metrics">
        <Metric
          name="Answer accuracy"
          value={pct(answerScore(e),2)}
          detail="Same questions as every other model; selected answers"
          large
        />
        <Metric
          name="Outputs passing checks"
          value={pct(m.coverage)}
          detail={`${num(m.valid)} valid / ${num(m.planned)} planned`}
        />
        <Metric
          name="Slower requests · P95"
          value={ms(m.p95_ms)}
          detail="All attempted quality requests"
        />
        <Metric
          name="Confidence mismatch"
          value={pct(m.ece)}
          detail={`${num(m.probability_count)} probability distributions`}
        />
      </div>
      <div className="results-grid">
        <section className="analysis-panel">
          <div className="section-title">
            <div>
              <h2>Does confidence match reality?</h2>
              <p>When this model says “80% confident”, is it right about 80% of the time? Only valid answers with probabilities are included.</p>
            </div>
            <span className="tag">CONFIDENCE GROUPS</span>
          </div>
          {!m.probability_count && <p className="small muted">This profile has no valid probability outputs for this chart. Empty bars are not evidence of 0% correctness.</p>}
          <svg
            viewBox="0 0 580 285"
            className="reliability-chart"
            role="img"
            aria-label="Confidence calibration chart"
          >
            {[0, 0.25, 0.5, 0.75, 1].map((v) => (
              <g key={v}>
                <line x1="50" x2="548" y1={245 - v * 210} y2={245 - v * 210} />
                <text x="40" y={249 - v * 210} textAnchor="end">
                  {v * 100}%
                </text>
              </g>
            ))}
            <path d="M50 245L548 35" className="ideal" />
            {m.reliability.map((b, i) => (
              <g key={i}>
                <rect
                  x={52 + i * 49.6}
                  y={245 - b.accuracy * 210}
                  width="37"
                  height={b.accuracy * 210}
                  className={b.count ? "bar" : "empty-bar"}
                />
                <text x={70 + i * 49.6} y="265" textAnchor="middle">
                  {(i + 1) * 10}
                </text>
                <text
                  x={70 + i * 49.6}
                  y={Math.max(22, 236 - b.accuracy * 210)}
                  textAnchor="middle"
                  className="bin-count"
                >
                  {b.count || ""}
                </text>
              </g>
            ))}
          </svg>
          <div className="chart-foot">
            <span>Across: stated confidence · height: actually correct</span>
            <span>Numbers above bars = answers in that group</span>
          </div><p className="small muted">Below the diagonal means too confident; above means too cautious. Empty groups mean no observations. These confidence estimates come from different methods and are not a universal ranking.</p>
        </section>
        <section className="analysis-panel">
          <div className="section-title">
            <div>
              <h2>Benchmark breakdown · correct + usable</h2>
              <p>Original strict scores, not the shared headline. Failed attempted requests count; unsupported inputs are excluded.</p>
            </div>
          </div>
          <div className="family-bars">
            {Object.entries(m.families).map(([name, f]) => (
              <div key={name}>
                <div>
                  <span>{name}</span>
                  <strong>{pct(f.correct / f.total)}</strong>
                </div>
                <div className="wide-track">
                  <i style={{ width: `${(f.correct / f.total) * 100}%` }} />
                </div>
                <small>
                  {f.correct} correct / {f.total} supported · {f.failed} failed
                </small>
              </div>
            ))}
          </div>
        </section>
      </div>
      <div className="results-grid">
        <section className="analysis-panel">
          <h2>Technical details · original scoring</h2>
          <div className="ledger">
            {[
              ["Macro F1", m.macro_f1?.toFixed(3)],
              ["Binary Brier", m.brier_binary?.toFixed(4)],
              ["Multiclass Brier", m.brier_multiclass?.toFixed(4)],
              ["Negative log loss", m.nll?.toFixed(4)],
              ["Expected-score MAE", m.ordinal_mae?.toFixed(4)],
              ["Answer matches · original supported set", pct(m.selected_label_accuracy)],
              ["Correct + usable · original supported set", pct(m.accuracy)],
              [
                "Reference output-contract failures",
                num(m.output_contract_failures),
              ],
              ["Unsupported", num(m.unsupported)],
              ["AI-teacher answers (excluded above)", num(m.teacher_count)],
              ["Correct + usable · shared questions", pct(e.matched?.accuracy)],
              [
                "Shared inputs, including AI-teacher cases",
                `${num(result.matched_count)} / ${num(result.case_count)}`,
              ],
              ["Shared answer-key questions", num(e.matched?.verified_count)],
            ].map(([a, b]) => (
              <div key={a}>
                <span>{a}</span>
                <strong>{b ?? "N/A"}</strong>
              </div>
            ))}
          </div>
          <p className="muted small">
            Strict accuracy requires the reference label and Arena's output
            contract. The post-hoc label-only diagnostic ignores output-contract
            validity on the same reference cases. The overview presents the existing shared-question label comparison for clarity; original strict scores remain available here.
          </p>
        </section>
        <section className="analysis-panel">
          <div className="section-title">
            <h2>Astra spot-check · separate from the score</h2>
            <span className="tag">CODEX CLI</span>
          </div>
          <div className="judge-summary">
            <ShieldCheck size={34} />
            <strong>
              {reviews.length}
              <span>judgments for this entrant</span>
            </strong>
          </div>
          <p className="muted">
            {reviews.length
              ? `${reviews.filter((j) => ["correct", "acceptable"].includes(j.data.grade?.verdict || "")).length} judged correct or acceptable in the audit sample. `
              : ""}
            Code compares all scored answers with the saved answer key. Astra reads a sample to flag ambiguity or questionable references. Its opinions do not change the accuracy above. Identical answers share one review; model names and answer keys are hidden.
          </p>
          <div className="audit-list">
            {reviews.slice(0, 3).map((j) => (
              <div key={j.job_id}>
                <span className="accent">
                  {label(j.data.grade?.verdict || "")}
                </span>
                <p>{j.data.grade?.rationale}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
      <Operations result={result} model={e.id} />
      <div className="limitations">
        <TriangleAlert size={18} />
        <div>
          <strong>Scope of these results</strong>
          {result.limitations.map((s) => (
            <p key={s}>{s}</p>
          ))}
          <p>
            Public teacher agreement is distinct from verified correctness. No
            overall winner is declared from a partial cohort.
          </p>
        </div>
      </div>
    </>
  );
}

function Cases({
  rid,
  models,
  result,
}: {
  rid: string | null;
  models: Model[];
  result: Result | null;
}) {
  const [data, setData] = useState<{
      total: number;
      cases: Case[];
      predictions: Prediction[];
    } | null>(null),
    [chosen, setChosen] = useState<string | null>(null),
    [search, setSearch] = useState(""),
    [pack, setPack] = useState(""),
    [offset, setOffset] = useState(0);

  useEffect(() => {
    if (rid)
      api<{ total: number; cases: Case[]; predictions: Prediction[] }>(
        `/runs/${rid}/cases?limit=100&offset=${offset}${pack ? "&pack=" + encodeURIComponent(pack) : ""}`,
      ).then(setData);
  }, [rid, offset, pack]);

  if (!rid || !data)
    return (
      <Empty
        icon={FlaskConical}
        title="The evidence lives here"
        detail="Each measured decision includes its exact state, available options, reference and model outputs."
      />
    );

  const filtered = data.cases.filter((c) =>
      (c.id + " " + c.state + " " + c.family)
        .toLowerCase()
        .includes(search.toLowerCase()),
    ),
    c = filtered.find((c) => c.id === chosen) || filtered[0];

  return (
    <div className="case-workspace">
      <aside className="case-list">
        <div className="search">
          <Search size={16} />
          <input
            aria-label="Search visible cases"
            placeholder="Search this page of cases…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          aria-label="Filter case pack"
          value={pack}
          onChange={(e) => {
            setPack(e.target.value);
            setOffset(0);
          }}
        >
          <option value="">All benchmark packs</option>
          {[
            "JevBench public",
            "Typed decisions",
            "Classification",
            "Multilingual",
            "RAG relevance",
            "Arena Fresh",
            "Robustness",
          ].map((p) => (
            <option key={p}>{p}</option>
          ))}
        </select>
        <div className="case-list-items">
          {filtered.map((item) => (
            <button
              key={item.id}
              className={c?.id === item.id ? "selected" : ""}
              onClick={() => setChosen(item.id)}
            >
              <span>
                {item.family}
                <small>
                  {item.pack} · {item.question.kind}
                </small>
              </span>
              <ChevronRight size={14} />
            </button>
          ))}
        </div>
        <div className="pagination">
          <button
            disabled={!offset}
            onClick={() => setOffset(Math.max(0, offset - 100))}
          >
            Previous
          </button>
          <span>
            {offset + 1}–{Math.min(offset + 100, data.total)} / {data.total}
          </span>
          <button
            disabled={offset + 100 >= data.total}
            onClick={() => setOffset(offset + 100)}
          >
            Next
          </button>
        </div>
      </aside>
      <section className="case-detail">
        {c ? (
          <>
            <div className="eyebrow">
              {c.pack} <span>/</span> {c.id}
            </div>
            <h2>{c.question.text}</h2>
            <div className="case-tags">
              <span className="tag">{c.question.kind.toUpperCase()}</span>
              <span className="tag">
                {c.label_status === "teacher" ? "AI-TEACHER ANSWER" : c.label_status === "formal" ? "RULE-DERIVED ANSWER" : "DATASET ANSWER KEY"}
              </span>
            </div>
            <div className="evidence-block">
              <CaseState text={c.state}/>
            </div>
            {c.question.rubric && (
              <div className="rubric">
                <span className="field-label">Decision rules / scoring instructions</span>
                <p>{c.question.rubric}</p>
              </div>
            )}
            <div className="reference">
              <CheckCircle2 size={18} />
              <span>Reference answer</span>
              <strong>{c.gold}</strong>
            </div>
            <h3>Model decisions</h3>
            <div className="decision-rows">
              {data.predictions
                .filter((p) => p.case_id === c.id)
                .map((p) => (
                  <div key={p.model_id}>
                    <div className="decision-title">
                      <strong>
                        {models.find((m) => m.id === p.model_id)?.name ||
                          p.model_id}
                      </strong>
                      <span
                        className={
                          p.status === "ok" && p.selected === c.gold
                            ? "accent"
                            : "muted"
                        }
                      >
                        {p.status === "ok" ? p.selected : label(p.status)}
                      </span>
                      <small>{ms(p.request_ms)}</small>
                    </div>
                    {p.probabilities && (
                      <div className="prob-bars">
                        {Object.entries(p.probabilities).map(([name, v]) => (
                          <div key={name}>
                            <span>{name}</span>
                            <div>
                              <i style={{ width: `${v * 100}%` }} />
                            </div>
                            <b>{pct(v)}</b>
                          </div>
                        ))}
                      </div>
                    )}
                    {p.error && <p className="muted">{p.error}</p>}
                    <small className="muted">
                      Probability source: {p.probability_source}
                    </small>
                  </div>
                ))}
            </div>
            {result?.judge_jobs
              .filter((j) => j.data.item.case_id === c.id && j.data.grade)
              .map((j) => (
                <div className="judge-case" key={j.job_id}>
                  <ShieldCheck size={17} />
                  <div>
                    <strong>Astra · {j.data.grade?.verdict}</strong>
                    <p>{j.data.grade?.rationale}</p>
                    <q>{j.data.grade?.evidence}</q>
                  </div>
                </div>
              ))}
          </>
        ) : (
          <Empty
            icon={Search}
            title={
              offline ? "Case text stays in the local run" : "No matching cases"
            }
            detail={
              offline
                ? "This shareable report includes metrics, judge verdicts and recorded workflows. Open the originating Arena workspace to inspect source text."
                : "Try a different search or benchmark pack."
            }
          />
        )}
      </section>
    </div>
  );
}

function Replay({
  rid,
  result,
}: {
  rid: string | null;
  result: Result | null;
}) {
  const [timeline, setTimeline] = useState<ArenaEvent[]>([]),
    [playing, setPlaying] = useState(false),
    [clock, setClock] = useState(0),
    [speed, setSpeed] = useState(1);

  useEffect(() => {
    setClock(0);
    setPlaying(false);
    if (rid) api<ArenaEvent[]>(`/runs/${rid}/timeline`).then(setTimeline);
  }, [rid]);

  const lanes = useMemo(() => {
    const values =
      result?.entrants.slice(0, 4).map((e) => ({
        id: e.id,
        name: e.name,
        events: timeline.filter(
          (t) => t.kind === "prediction" && t.data.model_id === e.id,
        ),
      })) || [];
    return values.map((v) => {
      let total = 0;
      return {
        ...v,
        points: v.events.map((t) => {
          total += Number(t.data.request_ms) || 0;
          return { time: total, event: t };
        }),
        total,
      };
    });
  }, [timeline, result]);

  const duration = Math.max(1, ...lanes.map((l) => l.total));

  useEffect(() => {
    if (!playing) return;
    const t = setInterval(
      () =>
        setClock((c) => {
          if (c + 100 * speed >= duration) {
            setPlaying(false);
            return duration;
          }
          return c + 100 * speed;
        }),
      100,
    );
    return () => clearInterval(t);
  }, [playing, speed, duration]);

  if (!rid || !result)
    return (
      <Empty
        icon={Play}
        title="A recording worth inspecting"
        detail="Finish an evaluation to replay actual decisions side by side, aligned at the first request."
      />
    );

  return (
    <>
      <div className="replay-controls">
        <span className="tag measured">RECORDED REPLAY</span>
        <span>Quality requests only · load and warmup excluded</span>
        <div>
          <button
            className="icon-btn"
            onClick={() => {
              setClock(0);
              setPlaying(false);
            }}
            aria-label="Restart replay"
          >
            <RotateCcw size={17} />
          </button>
          <button
            className="button primary compact"
            onClick={() => {
              if (clock === duration) setClock(0);
              setPlaying(!playing);
            }}
          >
            {playing ? <Pause size={16} /> : <Play size={16} />}{" "}
            {playing ? "Pause" : "Play"}
          </button>
          <select
            value={speed}
            aria-label="Replay speed"
            onChange={(e) => setSpeed(Number(e.target.value))}
          >
            {[0.5, 1, 2, 5, 10].map((n) => (
              <option value={n} key={n}>
                {n}×
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="replay-timer">
        <strong>
          {(clock / 1000).toFixed(1)}
          <small>s</small>
        </strong>
        <span>{speed}× playback · actual saved request durations</span>
      </div>
      <input
        className="timeline-slider"
        aria-label="Replay position"
        type="range"
        min="0"
        max={duration}
        value={clock}
        onChange={(e) => setClock(Number(e.target.value))}
      />
      <div className="replay-lanes">
        {lanes.map((lane, i) => {
          const done = lane.points.filter((p) => p.time <= clock),
            last = done.at(-1);
          return (
            <section key={lane.id}>
              <div className="lane-heading">
                <span>LANE {String(i + 1).padStart(2, "0")}</span>
                <h2>{lane.name}</h2>
              </div>
              <div className="lane-value">
                {String(done.length).padStart(2, "0")}
                <span>/ {lane.points.length} decisions</span>
              </div>
              <div className="decision-matrix">
                {lane.points.map((p, index) => (
                  <i
                    title={String(p.event.data.case_id)}
                    key={index}
                    className={
                      p.time <= clock
                        ? p.event.data.status === "ok"
                          ? "done"
                          : "failed"
                        : ""
                    }
                  />
                ))}
              </div>
              <div className="lane-current">
                <span className="field-label">LATEST DECISION</span>
                <strong>
                  {last
                    ? String(last.event.data.selected || last.event.data.status)
                    : "Waiting to start"}
                </strong>
                <small>
                  {last ? String(last.event.data.case_id) : "Aligned at t = 0"}
                </small>
              </div>
              <div className="lane-footer">
                <Timer size={15} />
                <span>{ms(lane.total)} total request time</span>
              </div>
            </section>
          );
        })}
      </div>
      <div className="limitations">
        <Activity size={18} />
        <p>
          These models ran sequentially on one GPU. This replay aligns their
          measured request sequences; it does not imply simultaneous inference.
          No model ranking is inferred from animation alone.
        </p>
      </div>
    </>
  );
}

function Setup({
  ready,
  selected,
  toggle,
  onRefresh,
  onError,
  onLocal,
}: {
  ready: Ready | null;
  selected: string[];
  toggle: (s: string) => void;
  onRefresh: () => Promise<void>;
  onError: (s: string) => void;
  onLocal: () => void;
}) {
  const [checking, setChecking] = useState(false);

  if (!ready)
    return (
      <Empty
        icon={Cpu}
        title="Inspecting this machine"
        detail="Checking the GPU, local runtimes and judge login."
      />
    );

  async function prepare() {
    try {
      await api("/setup/prepare", {
        model_ids: selected.filter(
          (m) => !ready?.models.find((x) => x.id === m)?.hosted,
        ),
      });
      await onRefresh();
    } catch (e) {
      onError((e as Error).message);
    }
  }

  async function check() {
    setChecking(true);
    try {
      await api("/setup/judge-check", {});
      await onRefresh();
    } catch (e) {
      onError((e as Error).message);
    } finally {
      setChecking(false);
    }
  }

  return (
    <>
      <div className="setup-summary">
        <div>
          <Cpu size={28} />
          <span>
            Compute
            <strong>
              {ready.hardware.gpu?.name || "No NVIDIA GPU detected"}
            </strong>
            <small>
              {num(ready.hardware.disk_free_gb)} GB free ·{" "}
              {ready.docker_ready
                ? "Worker image ready"
                : "Worker image required"}
            </small>
          </span>
        </div>
        <div>
          <Terminal size={28} />
          <span>
            Judge<strong>GPT-6 Astra · Codex CLI</strong>
            <small>
              {ready.judge.smoke_passed
                ? "Live smoke check passed"
                : ready.judge.ready
                  ? "ChatGPT login found; verify live call"
                  : "ChatGPT login required"}
            </small>
          </span>
          <button
            className="button secondary compact"
            onClick={check}
            disabled={checking || !!offline}
          >
            {checking ? "Checking…" : "Verify judge"}
          </button>
        </div>
      </div>
      <div className="section-title setup-title">
        <div>
          <h2>Model roster</h2>
          <p>
            Downloads are pinned, hashed and kept in your private local cache.
          </p>
        </div>
        <div className="heading-actions">
          <button className="button secondary compact" onClick={onLocal}>
            Use ready local models <ArrowRight size={15} />
          </button>
          <button
            className="button primary compact"
            onClick={prepare}
            disabled={ready.setup.status === "preparing" || !!offline}
          >
            <ArrowDownToLine size={16} />
            {ready.setup.status === "preparing"
              ? "Preparing…"
              : "Prepare selected"}
          </button>
        </div>
      </div>
      {ready.setup.message && (
        <div className="setup-progress">
          <Activity size={16} />
          {ready.setup.message}
        </div>
      )}
      <div className="table-scroll">
        <table className="setup-table">
          <thead>
            <tr>
              <th>ENTRANT</th>
              <th>EXECUTION</th>
              <th>REVISION</th>
              <th>LIMITS</th>
              <th>READINESS</th>
            </tr>
          </thead>
          <tbody>
            {ready.models.map((m) => (
              <tr key={m.id}>
                <td>
                  <label>
                    <input
                      type="checkbox"
                      checked={selected.includes(m.id)}
                      onChange={() => toggle(m.id)}
                    />
                    <div className="model-name">
                      {m.name}
                      <small>
                        {m.family} · {m.license}
                      </small>
                    </div>
                  </label>
                </td>
                <td>
                  {m.hosted ? "Hosted service" : m.size + " · " + m.precision}
                </td>
                <td className="mono">
                  {(m.resolved_revision || m.revision).slice(0, 12)}
                  {m.repo && (
                    <a
                      title="Open model card"
                      aria-label={`Open ${m.name} model card`}
                      href={`https://huggingface.co/${m.repo}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <ArrowUpRight size={12} />
                    </a>
                  )}
                </td>
                <td>
                  {m.max_options} options · {num(m.context)} tokens
                </td>
                <td>
                  <span className={m.ready ? "accent" : "muted"}>
                    {m.ready ? <Check size={13} /> : <Circle size={10} />}{" "}
                    {m.ready ? "Ready" : m.reason}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="setup-bottom">
        <section>
          <div className="section-title">
            <div>
              <h2>Frozen evaluation suite</h2>
              <p>
                {num(ready.suites.available)} / {num(ready.suites.expected)}{" "}
                decisions prepared
              </p>
            </div>
            <Database size={20} />
          </div>
          {ready.suites.packs.map((p) => (
            <div className="pack-row" key={p.name}>
              <span>
                {p.ready ? <CheckCircle2 size={15} /> : <Circle size={15} />}{" "}
                {p.name}
              </span>
              <strong>
                {num(p.available)} <small>/ {num(p.expected)}</small>
              </strong>
            </div>
          ))}
        </section>
        <section>
          <h2>Connections & provenance</h2>
          <div className="connection">
            <Terminal size={19} />
            <div>
              <strong>Codex CLI</strong>
              <p>
                {ready.judge.version || "Not installed"} · ChatGPT
                authentication
              </p>
              <small>
                Requested: gpt-6-astra
                <br />
                Observed model identifier:{" "}
                {ready.judge.observed_model || "not exposed by CLI events"}
              </small>
            </div>
          </div>
          <div className="connection">
            <Zap size={19} />
            <div>
              <strong>TypeSafe / Jev</strong>
              <p>
                {ready.models.find((m) => m.id === "jev")?.ready
                  ? "Server-side key configured"
                  : "Add TYPESAFE_API_KEY to your local .env file."}
              </p>
              <a href="https://typesafe.ai" target="_blank" rel="noreferrer">
                TypeSafe account <ExternalLink size={12} />
              </a>
            </div>
          </div>
          <p className="muted small">
            Keys stay on this machine. Reports exclude credentials and raw CLI
            logs. Third-party datasets are downloaded from their original
            sources.
          </p>
          <p className="muted small">{ready.suites.fresh_status}</p>
        </section>
      </div>
    </>
  );
}

function Empty({
  icon: Icon,
  title,
  detail,
}: {
  icon: typeof Activity;
  title: string;
  detail: string;
}) {
  return (
    <div className="empty-state">
      <Icon size={36} />
      <h2>{title}</h2>
      <p>{detail}</p>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
