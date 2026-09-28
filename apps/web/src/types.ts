export type Model = {
  id: string;
  name: string;
  family: string;
  size: string;
  hosted: boolean;
  diagnostic: boolean;
  ready: boolean;
  prepared: boolean;
  reason: string | null;
  revision: string;
  resolved_revision: string | null;
  precision: string;
  license: string;
  context: number;
  max_options: number;
  repo: string | null;
};
export type Metrics = {
  planned: number;
  completed: number;
  supported: number;
  verified_count: number;
  valid: number;
  correct: number;
  failed: number;
  unsupported: number;
  accuracy: number | null;
  selected_label_accuracy?: number | null;
  selected_label_correct?: number;
  output_contract_failures?: number;
  coverage: number;
  valid_rate: number | null;
  macro_f1: number | null;
  accuracy_ci: number[] | null;
  p50_ms: number | null;
  p95_ms: number | null;
  brier_binary: number | null;
  brier_multiclass: number | null;
  ece: number | null;
  nll: number | null;
  ordinal_mae: number | null;
  reliability: {
    lo: number;
    hi: number;
    count: number;
    confidence: number;
    accuracy: number;
  }[];
  families: Record<string, { total: number; correct: number; failed: number }>;
  probability_count: number;
  teacher_count: number;
  teacher_agreement?: number | null;
  teacher_brier?: number | null;
  pack_macro_accuracy?: number | null;
  diagnostics?: {
    rag: { queries: number; ndcg_at_10: number | null; mrr: number | null };
    coverage_error: {
      threshold: number;
      coverage: number;
      error: number | null;
    }[];
    robustness: Record<
      string,
      { pairs: number; accuracy_delta: number; answer_flip_rate: number }
    >;
  };
};
export type Run = {
  id: string;
  created: number;
  status: string;
  error: string | null;
  request: { preset: string; model_ids: string[]; judge: boolean };
  manifest: Record<string, unknown>;
};
export type Result = {
  manifest?: { case_sha256?: string };
  run_id: string;
  status: string;
  kind: string;
  preset: string;
  case_count: number;
  matched_count: number;
  entrants: {
    id: string;
    name: string;
    hosted: boolean;
    metrics: Metrics;
    matched: Metrics;
  }[];
  judge_jobs: {
    job_id: string;
    status: string;
    data: {
      grade?: { verdict: string; rationale: string; evidence: string };
      models: string[];
      item: { case_id: string };
      metadata?: { requested_model: string; observed_model: string | null };
    };
  }[];
  comparisons: {
    model: string;
    reference: string;
    n: number;
    delta: number;
    ci: number[];
  }[];
  limitations: string[];
  publication_ready: boolean;
  episodes?: Episode[];
  performance?: Record<
    string,
    {
      blocks: {
        block: number;
        concurrency: number;
        requests: number;
        valid: number;
        requests_per_second: number;
        p50_ms: number;
        p95_ms: number;
      }[];
      fanout: { questions: number; elapsed_ms: number }[];
    }
  >;
};
export type Ready = {
  hardware: {
    gpu: {
      name: string;
      memory_total_mb: number;
      memory_used_mb: number;
      temperature_c: number;
      power_w: number;
      driver: string;
    } | null;
    platform: string;
    disk_free_gb: number;
  };
  models: Model[];
  docker_ready: boolean;
  judge: {
    ready: boolean;
    requested_model: string;
    observed_model: string | null;
    smoke_passed?: boolean;
    version?: string;
    reason?: string;
  };
  suites: {
    expected: number;
    available: number;
    packs: {
      name: string;
      expected: number;
      available: number;
      ready: boolean;
    }[];
    fresh_status: string;
    presets: { id: string; count: number; ready: boolean }[];
  };
  active_run: string | null;
  setup: { status?: string; message?: string };
};
export type Prediction = {
  case_id: string;
  model_id: string;
  status: string;
  selected: string | null;
  probabilities: Record<string, number> | null;
  request_ms: number;
  error: string | null;
  probability_source: string;
  raw: unknown;
};
export type Case = {
  id: string;
  cluster: string;
  pack: string;
  family: string;
  state: string;
  question: { text: string; kind: string; labels: string[]; rubric: string };
  gold: string;
  label_status: string;
  evidence: string;
  provenance: Record<string, unknown>;
};
export type ArenaEvent = {
  id: number;
  time: number;
  kind: string;
  data: Record<string, unknown>;
};
export type Episode = {
  model_id: string;
  task: string;
  seed: number;
  mode: string;
  success: boolean;
  steps: number;
  violations: number;
  reward: number;
  wall_request_ms: number;
  deadline_misses: number | null;
  blocked?: number[][];
  goal?: number[];
  trace: {
    step: number;
    before?: number[];
    after?: number[];
    answer: string | null;
    request_ms: number;
    valid?: boolean;
    correct?: boolean;
    topic?: string;
    restricted?: boolean;
    deadline_missed?: boolean;
  }[];
};
