import { useEffect, useMemo, useState } from "react";
import {
  Box,
  Play,
  Pause,
  RotateCcw,
  Timer,
  ArrowRight,
  Check,
  TriangleAlert,
} from "lucide-react";
import type { Result, Episode } from "./types";
import referenceCautions from "../../../docs/reference-cautions.json";

const time = (n: number) =>
  n >= 1000 ? `${(n / 1000).toFixed(2)}s` : `${n.toFixed(0)}ms`;
const pct = (n: number | null | undefined) =>
  n == null ? "N/A" : `${(100 * n).toFixed(1)}%`;

export function Operations({
  result,
  model,
}: {
  result: Result;
  model: string;
}) {
  const perf = result.performance?.[model],
    episodes = (result.episodes || []).filter((e) => e.model_id === model);
  const m = result.entrants.find((e) => e.id === model)?.metrics;
  const caution = referenceCautions.applicability.find(
    (profile) => profile.case_sha256 === result.manifest?.case_sha256,
  );
  return (
    <>
      <section className="analysis-panel operation-panel">
        <div className="section-title">
          <div>
            <h2>Performance, measured separately.</h2>
            <p>
              Three serial blocks over the first 200 frozen JevBench public
              cases; loading and warmup excluded.
            </p>
          </div>
          <span className="tag">{perf ? "MEASURED" : "FULL SUITE ONLY"}</span>
        </div>
        {perf ? (
          <>
            <div className="performance-blocks">
              {perf.blocks.map((b) => (
                <div key={b.block}>
                  <span>
                    BLOCK {b.block + 1} · CONCURRENCY {b.concurrency}
                  </span>
                  <strong>
                    {b.requests_per_second.toFixed(1)}
                    <small> decisions / sec</small>
                  </strong>
                  <div>
                    <span>Typical {time(b.p50_ms)}</span>
                    <span>95% within {time(b.p95_ms)}</span>
                    <span>
                      {b.valid}/{b.requests} valid
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="fanout">
              {perf.fanout.map((f) => (
                <span key={f.questions}>
                  <b>{f.questions}</b> repeated questions / same state{" "}
                  <ArrowRight size={13} />
                  <strong>{time(f.elapsed_ms)}</strong>
                </span>
              ))}
            </div>
            <p className="small muted">
              Serial dispatch profile. Concurrency 4/16 and native batch
              acceleration are not measured.
            </p>
          </>
        ) : (
          <p className="muted small">
            Run the Full suite to collect three 200-request timing blocks,
            same-state fanout and three load/unload cycles.
          </p>
        )}
      </section>
      <section className="analysis-panel operation-panel">
        <div className="section-title">
          <div>
            <h2>Paired comparisons</h2>
            <p>
              Difference in strict correctness on each pair’s supported reference cases.
              Denominators can differ from the all-entrant shared label table.
              Descriptive 95% intervals; positive favors this entrant.
            </p>
          </div>
        </div>
        {result.comparisons.filter((c) => c.model === model).length ? (
          <div className="ledger">
            {result.comparisons
              .filter((c) => c.model === model)
              .map((c) => (
                <div key={c.reference}>
                  <span>
                    Versus{" "}
                    {result.entrants.find((e) => e.id === c.reference)?.name ||
                      c.reference}{" "}
                    · {c.n.toLocaleString()} paired cases
                  </span>
                  <strong>
                    {c.delta == null
                      ? "N/A"
                      : `${c.delta >= 0 ? "+" : ""}${(c.delta * 100).toFixed(1)} pp`}
                    {c.ci && (
                      <small>
                        {" "}
                        ({(c.ci[0] * 100).toFixed(1)} to{" "}
                        {(c.ci[1] * 100).toFixed(1)})
                      </small>
                    )}
                  </strong>
                </div>
              ))}
          </div>
        ) : (
          <p className="muted small">
            Select another entrant in a completed run containing Jev or Qwen to
            inspect a paired comparison.
          </p>
        )}
      </section>
      <div className="results-grid">
        <section className="analysis-panel">
          <h2>Reference agreement & retrieval</h2>
          <div className="ledger">
            <div>
              <span>Agreement with AI-teacher answers (separate)</span>
              <strong>{pct(m?.teacher_agreement)}</strong>
            </div>
            <div>
              <span>Difference from AI-teacher probabilities</span>
              <strong>{m?.teacher_brier?.toFixed(4) ?? "N/A"}</strong>
            </div>
            <div>
              <span>Pack macro accuracy</span>
              <strong>{pct(m?.pack_macro_accuracy)}</strong>
            </div>
            <div>
              <span>SciFact nDCG@10 / fixed pool</span>
              <strong>
                {m?.diagnostics?.rag.ndcg_at_10?.toFixed(3) ?? "N/A"}
              </strong>
            </div>
            <div>
              <span>SciFact MRR / fixed pool</span>
              <strong>{m?.diagnostics?.rag.mrr?.toFixed(3) ?? "N/A"}</strong>
            </div>
            <div>
              <span>Complete query pools</span>
              <strong>{m?.diagnostics?.rag.queries || 0}</strong>
            </div>
          </div>
        </section>
        <section className="analysis-panel">
          <h2>Workflow outcomes</h2>
          {episodes.length ? (
            ["untimed_quality", "deadline_500ms"]
              .filter((mode) => episodes.some((e) => e.mode === mode))
              .map((mode) => {
                const rows = episodes.filter((e) => e.mode === mode);
                const ticketEpisodes = rows.filter((e) => e.task === "tickets");
                const warehouseEpisodes = rows.filter(
                  (e) => e.task === "warehouse",
                );
                const tickets = ticketEpisodes.flatMap((e) => e.trace);
                const unrestricted = tickets.filter((step) => !step.restricted);
                return (
                  <div className="episode-score" key={mode}>
                    <span>
                      {mode === "untimed_quality"
                        ? "Untimed quality"
                        : "500ms decision deadline"}
                    </span>
                    <strong>
                      {rows.filter((e) => e.success).length}
                      <small> / {rows.length} successful episodes</small>
                    </strong>
                    <p>
                      Warehouse:{" "}
                      {warehouseEpisodes.filter((e) => e.success).length}/
                      {warehouseEpisodes.length}
                      {" · "}Tickets:{" "}
                      {ticketEpisodes.filter((e) => e.success).length}/
                      {ticketEpisodes.length}
                    </p>
                    <p>
                      Ticket decisions:{" "}
                      {tickets.filter((step) => step.correct).length}/
                      {tickets.length} correct. Unrestricted tickets sent to
                      Review:{" "}
                      {
                        unrestricted.filter((step) => step.answer === "Review")
                          .length
                      }
                      /{unrestricted.length}.
                    </p>
                    <p>
                      {rows.reduce((s, e) => s + e.violations, 0)} constraint
                      violations ·{" "}
                      {rows.reduce((s, e) => s + (e.deadline_misses || 0), 0)}{" "}
                      deadline misses
                    </p>
                  </div>
                );
              })
          ) : (
            <p className="small muted spaced">
              Demo and Full runs include recorded warehouse and ticket-routing
              episodes.
            </p>
          )}
          <p className="small muted">
            Ticket success requires all 12 decisions correct. Repeated blocked
            moves count at each step; they are not independent failures.
          </p>
        </section>
      </div>
      {m?.diagnostics && (
        <div className="results-grid">
          <section className="analysis-panel">
            <h2>Confidence / coverage</h2>
            <p className="small muted spaced">
              Coverage is retained valid reference answers divided by all
              {" "}{result.case_count.toLocaleString()} planned records; teacher
              records are in the denominator but are not eligible. These are
              descriptive test thresholds, not calibrated deployment settings.
            </p>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>MIN CONFIDENCE</th>
                    <th>COVERAGE</th>
                    <th>ERROR</th>
                  </tr>
                </thead>
                <tbody>
                  {m.diagnostics.coverage_error.map((r) => (
                    <tr key={r.threshold}>
                      <td>{pct(r.threshold)}</td>
                      <td>{pct(r.coverage)}</td>
                      <td>{pct(r.error)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <section className="analysis-panel">
            <h2>What happens when the input changes?</h2>
            <p className="small muted spaced">
              Each changed input is compared with its original. Harmless edits should preserve the answer; changing a decisive fact should change it.
            </p>
            <div className="ledger">
              {Object.entries(m.diagnostics.robustness).map(([name, r]) => (
                <div key={name}>
                  <span>
                    {name} · {r.pairs} pairs
                  </span>
                  <strong>
                    {(r.accuracy_delta * 100).toFixed(1)} pp
                    <small> · {pct(r.answer_flip_rate)} answer flips</small>
                  </strong>
                </div>
              ))}
            </div>
          </section>
        </div>
      )}
      {caution && (
        <section className="analysis-panel operation-panel">
          <div className="section-title">
            <h2>Reference wording under review</h2>
            <TriangleAlert size={18} />
          </div>
          <p className="small muted">
            {caution.affected_cases} cases in this frozen suite combine a
            payment or onboarding topic with the service marked unavailable. The reference
            routes by topic; Engineering is a plausible alternate reading. This
            was found after the Demo. Original scores stay unchanged; exclusions
            belong only in a separately labeled sensitivity analysis. Judge
            agreement does not settle that ambiguity.
          </p>
        </section>
      )}
    </>
  );
}

export function EpisodeReplay({ result }: { result: Result }) {
  const episodes = result.episodes || [];
  const [task, setTask] = useState("warehouse"),
    [seed, setSeed] = useState(5090),
    [mode, setMode] = useState("untimed_quality"),
    [chosen, setChosen] = useState<string[]>([]),
    [playing, setPlaying] = useState(false),
    [clock, setClock] = useState(0),
    [speed, setSpeed] = useState(1);
  const available = result.entrants.filter((e) =>
    episodes.some((p) => p.model_id === e.id),
  );
  useEffect(() => {
    setChosen([]);
    setClock(0);
    setPlaying(false);
  }, [result.run_id]);
  useEffect(() => {
    setChosen((old) =>
      old.length
        ? old
        : [
            "laya",
            "decider",
            "winnow",
            "nimble",
            "plumb",
            "semif",
            "clm",
            "qwen",
            "nli",
            "laya-typed",
            "laya-multi",
            "uniform",
          ]
            .filter((id) => available.some((e) => e.id === id))
            .slice(0, 4),
    );
  }, [result.run_id, episodes.length]);
  const lanes = useMemo(
    () =>
      available
        .filter((e) => chosen.includes(e.id))
        .map((e) => ({
          name: e.name,
          episode: episodes.find(
            (p) =>
              p.model_id === e.id &&
              p.task === task &&
              p.seed === seed &&
              p.mode === mode,
          ),
        }))
        .filter((e) => e.episode)
        .map((e) => {
          let elapsed = 0;
          return {
            ...e,
            episode: e.episode!,
            points: e.episode!.trace.map((t) => ({
              time: (elapsed += t.request_ms),
              step: t,
            })),
            duration: e.episode!.wall_request_ms,
          };
        }),
    [episodes, chosen, task, seed, mode],
  );
  const duration = Math.max(1, ...lanes.map((l) => l.duration));
  useEffect(() => {
    setClock(0);
    setPlaying(false);
  }, [task, seed, mode, chosen]);
  useEffect(() => {
    if (!playing) return;
    const timer = setInterval(
      () =>
        setClock((t) => {
          const n = Math.min(duration, t + 50 * speed);
          if (n === duration) setPlaying(false);
          return n;
        }),
      50,
    );
    return () => clearInterval(timer);
  }, [playing, speed, duration]);
  if (!episodes.length)
    return (
      <div className="empty-state">
        <Box size={36} />
        <h2>The same world. Different decisions.</h2>
        <p>
          Run Demo or Full to record warehouse navigation and ticket routing.
          Every seed stays available for replay.
        </p>
      </div>
    );
  return (
    <>
      <section className="replay-intro"><h2>Two workflow demos, many saved scenarios</h2><p>These tabs are task types: moving through a warehouse and routing support tickets. Full v2 recorded 20 scenarios per task, per model, both untimed and with a 500 ms deadline — 1,040 episodes in total. They are separate from the 7,671 static benchmark questions in Case explorer.</p><p className="small muted">Playback uses saved decisions. It does not rerun models, spend credits or change results. These simple environments show how decisions combine across steps; they do not prove deployment success.</p></section>
      <div className="episode-controls">
        <div className="workspace-tabs">
          {["warehouse", "tickets"].map((t) => (
            <button
              key={t}
              className={task === t ? "selected" : ""}
              onClick={() => setTask(t)}
            >
              {t === "warehouse" ? "Warehouse dispatch" : "Ticket routing"}
            </button>
          ))}
        </div>
        <div>
          <select
            aria-label="Episode seed"
            value={seed}
            onChange={(e) => setSeed(+e.target.value)}
          >
            {[...new Set(episodes.map((e) => e.seed))].sort().map((s) => (
              <option key={s} value={s}>
                Seed {s}
              </option>
            ))}
          </select>
          <select
            aria-label="Episode mode"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
          >
            {[...new Set(episodes.map((e) => e.mode))].map((m) => (
              <option key={m} value={m}>
                {m === "untimed_quality" ? "Untimed quality" : "500ms deadline"}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="lane-picker">
        {available.map((e) => (
          <button
            key={e.id}
            className={chosen.includes(e.id) ? "selected" : ""}
            onClick={() =>
              setChosen((c) =>
                c.includes(e.id)
                  ? c.filter((x) => x !== e.id)
                  : c.length < 4
                    ? [...c, e.id]
                    : [...c.slice(1), e.id],
              )
            }
          >
            {chosen.includes(e.id) && <Check size={12} />} {e.name}
          </button>
        ))}
        <span>Choose up to four lanes</span>
      </div>
      <div className="replay-controls">
        <span className="tag measured">RECORDED WORKFLOWS</span>
        <span>Sequential inference · aligned at zero · {speed}× playback</span>
        <div>
          <button
            className="icon-btn"
            aria-label="Restart episode replay"
            onClick={() => {
              setClock(0);
              setPlaying(false);
            }}
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
            aria-label="Episode playback speed"
            value={speed}
            onChange={(e) => setSpeed(+e.target.value)}
          >
            {[0.1, 0.25, 0.5, 1, 2, 5, 10].map((n) => (
              <option key={n}>{n}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="replay-timer">
        <strong>
          {(clock / 1000).toFixed(2)}
          <small>s</small>
        </strong>
        <span>{time(duration)} recorded · real request durations</span>
      </div>
      <input
        className="timeline-slider"
        aria-label="Episode playback position"
        type="range"
        min={0}
        max={duration}
        value={clock}
        onChange={(e) => setClock(+e.target.value)}
      />
      <div
        className="world-lanes"
        style={{
          gridTemplateColumns: `repeat(${Math.max(1, lanes.length)},minmax(0,1fr))`,
        }}
      >
        {lanes.map((l, i) => {
          const done = l.points.filter((p) => p.time <= clock),
            last = done.at(-1)?.step,
            finished = done.length === l.points.length;
          return (
            <section key={l.episode.model_id}>
              <div className="world-title">
                <span>LANE {String(i + 1).padStart(2, "0")}</span>
                <h2>{l.name}</h2>
                <span className="tag">
                  {finished
                    ? l.episode.success
                      ? "SUCCESS"
                      : "INCOMPLETE"
                    : `STEP ${done.length} / ${l.points.length}`}
                </span>
              </div>
              {task === "warehouse" ? (
                <WarehouseGrid
                  episode={l.episode}
                  steps={done.map((d) => d.step)}
                />
              ) : (
                <TicketBoard
                  episode={l.episode}
                  steps={done.map((d) => d.step)}
                />
              )}
              <div className="world-decision">
                <span>LATEST DECISION</span>
                <strong>
                  {last?.answer || "—"}
                  {last?.deadline_missed && <TriangleAlert size={16} />}
                </strong>
                <small>
                  {last
                    ? `${time(last.request_ms)}${last.deadline_missed ? " · deadline missed" : ""}`
                    : "Waiting for first request"}
                </small>
              </div>
              <div className="world-metrics">
                <span>
                  <b>{done.length}</b> steps
                </span>
                <span>
                  <b>
                    {
                      done.filter(
                        (d) =>
                          d.step.valid === false || d.step.correct === false,
                      ).length
                    }
                  </b>{" "}
                  failed actions
                </span>
                <span>
                  <Timer size={13} />{" "}
                  {finished ? time(l.duration) : time(clock)}
                </span>
              </div>
            </section>
          );
        })}
      </div>
      <p className="muted small spaced">
        In deadline mode, a late answer consumes a step and causes no action.
        The environment pauses for each decision in untimed mode. These are
        deterministic simulations, not external actions.
      </p>
    </>
  );
}

function WarehouseGrid({
  episode,
  steps,
}: {
  episode: Episode;
  steps: Episode["trace"];
}) {
  const position = steps.at(-1)?.after || [0, 0],
    goal = episode.goal || [5, 5],
    path = [[0, 0], ...steps.map((t) => t.after || [0, 0])];
  return (
    <svg
      viewBox="0 0 300 300"
      className="warehouse-grid"
      role="img"
      aria-label={`Warehouse robot at ${position.join(",")}, goal ${goal.join(",")}`}
    >
      <defs>
        <pattern
          id={`grid-${episode.model_id}`}
          width="50"
          height="50"
          patternUnits="userSpaceOnUse"
        >
          <rect
            width="50"
            height="50"
            fill="none"
            stroke="var(--line)"
            strokeWidth="1"
          />
        </pattern>
      </defs>
      <rect width="300" height="300" fill={`url(#grid-${episode.model_id})`} />
      {(episode.blocked || []).map(([x, y]) => (
        <g key={`${x}-${y}`}>
          <rect
            x={x * 50 + 5}
            y={y * 50 + 5}
            width="40"
            height="40"
            rx="3"
            fill="var(--obstacle)"
          />
          <path
            d={`M${x * 50 + 12} ${y * 50 + 12}l26 26m0-26l-26 26`}
            stroke="#55555c"
          />
        </g>
      ))}
      <rect
        x={goal[0] * 50 + 7}
        y={goal[1] * 50 + 7}
        width="36"
        height="36"
        rx="4"
        fill="var(--accent-soft)"
        stroke="var(--accent)"
        strokeDasharray="3 3"
      />
      <text
        x={goal[0] * 50 + 25}
        y={goal[1] * 50 + 29}
        textAnchor="middle"
        fill="var(--accent)"
        fontSize="10"
      >
        GOAL
      </text>
      <polyline
        points={path
          .map((p) => `${p[0] * 50 + 25},${p[1] * 50 + 25}`)
          .join(" ")}
        fill="none"
        stroke="var(--accent)"
        strokeWidth="3"
        opacity=".45"
      />
      <circle
        cx={position[0] * 50 + 25}
        cy={position[1] * 50 + 25}
        r="15"
        fill="var(--accent-soft)"
      />
      <circle
        cx={position[0] * 50 + 25}
        cy={position[1] * 50 + 25}
        r="8"
        fill="var(--accent)"
      />
      <circle cx={25} cy={25} r="3" fill="var(--ink)" />
    </svg>
  );
}

function TicketBoard({
  episode,
  steps,
}: {
  episode: Episode;
  steps: Episode["trace"];
}) {
  const active = steps.at(-1);
  return (
    <div className="ticket-world">
      <div className="ticket-feed">
        <span>
          INCOMING / {steps.length} OF {episode.steps}
        </span>
        <strong>{active?.topic || "Awaiting first ticket"}</strong>
        <small>
          {active?.restricted
            ? "Restricted account · review required"
            : "Route using the supplied policy"}
        </small>
      </div>
      <ArrowRight className="ticket-arrow" size={20} />
      <div className="ticket-queues">
        {["Billing", "Engineering", "Success", "Review"].map((queue) => (
          <div
            key={queue}
            className={active?.answer === queue ? "selected" : ""}
          >
            <span>{queue}</span>
            <strong>{steps.filter((s) => s.answer === queue).length}</strong>
            <div className="queue-dots">
              {steps
                .filter((s) => s.answer === queue)
                .map((s, i) => (
                  <i key={i} className={s.correct ? "correct" : "incorrect"} />
                ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
