// Types mirror crates/api/src/views.rs and crates/runner/src/result.rs.

export type Band = "easy" | "medium" | "hard";
export type Mode = "write" | "fix" | "stage";
export type Section = "D" | "L" | "S" | "C" | "Y" | "B" | "M";
export type Tier = "core" | "light" | "sde3";
export type ContentStatus = "draft" | "ready";
export type Progress = "not_started" | "started" | "solved" | "assisted";

export interface StageView {
  slug: string;
  name: string;
  band: Band;
  total: number;
  ready: number;
  solved: number;
}

export interface TrackSummary {
  code: string;
  slug: string;
  name: string;
  section: Section;
  tier: Tier;
  order: number;
  summary: string;
  stages: StageView[];
  total: number;
  ready: number;
  solved: number;
}

export interface ProblemSummary {
  id: string;
  slug: string;
  title: string;
  mode: Mode;
  level: Band;
  stage: string;
  order: number;
  status: ContentStatus;
  tags: string[];
  progress: Progress;
}

export interface TrackDetail extends TrackSummary {
  problems: ProblemSummary[];
}

export interface Hint {
  kind: string;
  text: string;
}

export interface Rules {
  forbid_methods: string[];
  forbid_types: string[];
  forbid_unsafe: boolean;
  max_changed_lines: number | null;
}

export interface SolutionView {
  unlocked: boolean;
  code: string | null;
  notes: { explanation: string; time: string; space: string } | null;
}

export interface AttemptView {
  started: boolean;
  started_at: string | null;
  solved: boolean;
  assisted: boolean;
  hints_revealed: number;
  solution_revealed: boolean;
}

export type RunStatus = "passed" | "failed" | "compile_error" | "timeout";
export type Level = "error" | "warning" | "note" | "help";

export interface Span {
  file: string;
  line_start: number;
  line_end: number;
  col_start: number;
  col_end: number;
  primary: boolean;
  label: string | null;
}

export interface Diagnostic {
  level: Level;
  code: string | null;
  message: string;
  rendered: string;
  spans: Span[];
  notes: string[];
}

export interface TestOutcome {
  suite: "visible" | "hidden";
  name: string;
  outcome: "passed" | "failed" | "ignored" | "timed_out";
  duration_ms: number | null;
  check: { input: string; expected: string; got: string } | null;
  panic: string | null;
  stdout: string;
}

export interface RunView {
  id: number;
  kind: "run" | "submit";
  created_at: string;
  code: string;
  status: RunStatus;
  passed: number;
  total: number;
  duration_ms: number;
  diagnostics: Diagnostic[];
  tests: TestOutcome[];
  /** Fix-this rules broken; any one keeps a submit from solving the problem. */
  violations: Violation[];
}

export interface Violation {
  rule: string;
  message: string;
  line: number | null;
}

export interface ProblemDetail {
  id: string;
  slug: string;
  title: string;
  mode: Mode;
  level: Band;
  status: ContentStatus;
  track: { code: string; slug: string; name: string; section: Section };
  stage: { slug: string; name: string; band: Band; number: number; position: number; count: number };
  position: number;
  count: number;
  prev: string | null;
  next: string | null;
  statement: string;
  tags: string[];
  teaches: string[];
  constraints: string[];
  examples: { input: string; output: string }[];
  follow_up: string | null;
  related: string[];
  rules: Rules | null;
  starter: string;
  draft: string | null;
  visible_tests: string;
  hints: { total: number; revealed: Hint[]; locked: string[] };
  solution: SolutionView;
  attempt: AttemptView;
  runs: RunView[];
}

export interface RunOutcome {
  run: RunView;
  attempt: AttemptView;
  solution: SolutionView;
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body === undefined ? undefined : { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: "unknown", message: res.statusText }));
    throw new ApiError(res.status, err.error ?? "unknown", err.message ?? res.statusText);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

export const api = {
  tracks: () => request<TrackSummary[]>("GET", "/tracks"),
  track: (slug: string) => request<TrackDetail>("GET", `/tracks/${slug}`),
  problem: (id: string) => request<ProblemDetail>("GET", `/problems/${id}`),
  saveDraft: (id: string, code: string) => request<void>("PUT", `/problems/${id}/draft`, { code }),
  reset: (id: string) => request<ProblemDetail>("DELETE", `/problems/${id}/draft`),
  run: (id: string, code: string) => request<RunOutcome>("POST", `/problems/${id}/run`, { code }),
  submit: (id: string, code: string) => request<RunOutcome>("POST", `/problems/${id}/submit`, { code }),
  revealHint: (id: string) => request<ProblemDetail>("POST", `/problems/${id}/hints`),
  revealSolution: (id: string) => request<ProblemDetail>("POST", `/problems/${id}/solution`),
};
