// Types mirror crates/api/src/views.rs and crates/runner/src/result.rs.

export type Band = "easy" | "medium" | "hard";
export type Mode = "write" | "fix" | "stage";
export type Section = "D" | "L" | "S" | "C" | "Y" | "F" | "B" | "M";
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
  /** 0–100: weighted by level, assisted solves count half. */
  readiness: number;
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
  /** Companies known to ask it, FAANG first. */
  companies: string[];
  progress: Progress;
}

export interface CompanyGroup {
  name: string;
  companies: string[];
}

export interface TrackDetail extends TrackSummary {
  problems: ProblemSummary[];
  /** Every taggable company, grouped (FAANG, Big tech, Databases, Rust shops) and in display order. */
  company_groups: CompanyGroup[];
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
  /** A scheduled re-solve rather than the first time through. */
  resolve: boolean;
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
  companies: string[];
  teaches: string[];
  constraints: string[];
  examples: { input: string; output: string }[];
  follow_up: string | null;
  related: string[];
  /** Crates the problem may use, e.g. ["tokio", "serde"]. */
  crates: string[];
  rules: Rules | null;
  starter: string;
  draft: string | null;
  /** The scratch main.rs for Run. */
  scratch: string;
  visible_tests: string;
  /** The hidden tests' source, once the problem has been solved; null before. */
  hidden_tests: string | null;
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

export interface Activity {
  streak: number;
  week: { date: string; solved: number }[];
  week_solved: number;
  week_unassisted: number;
  recent: {
    problem_id: string;
    title: string;
    track: string;
    outcome: "solved" | "assisted" | "failing" | "started";
    detail: string;
    at: string;
  }[];
  next: NextUp | null;
}

export interface NextUp {
  problem_id: string;
  title: string;
  mode: Mode;
  level: Band;
  track_code: string;
  track_slug: string;
  track_name: string;
  stage_name: string;
  reason: "resume" | "current" | "start";
  /** First paragraph of the statement, markdown. */
  excerpt: string;
  readiness: number;
  gain: number;
}

export interface EditorSettings {
  font_size: number;
  font_family: string;
  vim: boolean;
  /** Workspace status-bar toggles. */
  autocomplete: boolean;
  rust_analyzer: boolean;
  borrow_lanes: boolean;
  /** rust-analyzer checks with clippy, so lints show while editing. */
  live_clippy: boolean;
  /** rustfmt after a 1.5 s pause in typing, not only on ⌘S / ⇧⌥F. */
  format_on_pause: boolean;
}

export type Accent = "copper" | "rose" | "sky" | "teal";

export interface AppearanceSettings {
  accent: Accent;
}

export interface Settings {
  editor: EditorSettings;
  appearance: AppearanceSettings;
  accents: Accent[];
  font_families: string[];
  font_sizes: [number, number];
}

export interface ProgressOverview {
  streak: number;
  longest_streak: number;
  heat_start: string;
  heat: number[];
  solved_year: number;
  active_days_year: number;
  unassisted_30d: number | null;
  unassisted_prev_30d: number | null;
  focus_week_seconds: number;
  focus_quarter_seconds: number;
  weekly: { week_start: string; easy: number; medium: number; hard: number }[];
  readiness_trend: { area: "dsa" | "rust" | "build"; points: (number | null)[] }[];
  this_week: { date: string; solved: number; unassisted: number; focus_seconds: number }[];
  by_section: { section: Section; solved: number; written: number; readiness: number | null }[];
}

export interface Counted {
  key: string;
  message: string;
  count: number;
  where_most: string | null;
}

export interface ProgressStats {
  first_run_pass: number | null;
  runs_per_solve: number | null;
  runs_per_solve_hard: number | null;
  compile_error_rate: number | null;
  within_budget: number | null;
  errors: Counted[];
  lints: Counted[];
  rules: Counted[];
  timing: { level: Band; mode: Mode; budget_minutes: number; median_minutes: number | null; within_budget: number | null; solved: number }[];
}

export interface ReviewItem {
  problem_id: string;
  title: string;
  track: string;
  level: Band;
  step: number;
  interval_days: number;
  due_at: string;
  days_overdue: number;
  last_result: "unassisted" | "assisted";
}

export interface ReviewsView {
  due_today: number;
  overdue: number;
  minutes_today: number;
  retention_30d: number | null;
  in_rotation: number;
  graduated: number;
  queue: ReviewItem[];
  forecast: number[];
}

export interface ScratchResult {
  status: "ok" | "exited" | "compile_error" | "timeout";
  diagnostics: Diagnostic[];
  stdout: string;
  stderr: string;
  exit_code: number | null;
  duration_ms: number;
}

// ---------------------------------------------------------------- AI assistant

export interface AiInfo {
  provider: "gemini" | "openai" | "anthropic";
  model: string;
  /** `provider/model`, or null when no embedding provider is configured. */
  embeddings: string | null;
}

export interface AiStatus {
  enabled: boolean;
  info?: AiInfo;
  indexed_problems: number;
  indexed_attempts: number;
}

export interface AiSource {
  kind: "problem" | "code" | "run" | "reference" | "similar" | "attempt" | "stats";
  label: string;
  problem_id?: string;
}

export interface AiMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  action: string | null;
  sources: AiSource[];
  created_at: string;
}

export type AiAction = "explain_error" | "hint" | "complexity" | "similar" | "review";

export interface AiPattern {
  kind: "error" | "lint" | "strength" | "time" | "habit";
  label: string;
  title: string;
  detail: string;
  evidence: string;
}

export interface PatternsReport {
  summary: string;
  patterns: AiPattern[];
  time_split: { label: string; percent: number }[];
  next: { problem_id: string; title: string; track: string; reason: string }[];
  based_on: { attempts: number; runs: number };
  generated_at: string;
  model: string;
}

export interface AiChatEvents {
  sources?: (s: AiSource[]) => void;
  /** This question marked the attempt assisted. */
  assisted?: () => void;
  chunk: (text: string) => void;
  done?: () => void;
}

/** Streams an answer (server-sent events over a POST, which EventSource can't do). */
export async function aiChat(
  id: string,
  body: { message?: string; action?: AiAction; code?: string },
  on: AiChatEvents,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`/api/ai/chat/${id}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok || !res.body) {
    const err = await res.json().catch(() => ({ error: "unknown", message: res.statusText }));
    throw new ApiError(res.status, err.error ?? "unknown", err.message ?? res.statusText);
  }
  const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    let cut: number;
    while ((cut = buffer.indexOf("\n\n")) >= 0) {
      const block = buffer.slice(0, cut);
      buffer = buffer.slice(cut + 2);
      let event = "message";
      const data: string[] = [];
      for (const line of block.split("\n")) {
        if (line.startsWith("event:")) event = line.slice(6).trim();
        else if (line.startsWith("data:")) data.push(line.slice(5).replace(/^ /, ""));
      }
      const payload = data.join("\n");
      if (event === "sources") on.sources?.(JSON.parse(payload) as AiSource[]);
      else if (event === "assisted") on.assisted?.();
      else if (event === "chunk") on.chunk(JSON.parse(payload) as string);
      else if (event === "done") on.done?.();
      else if (event === "error") throw new ApiError(502, "ai_failed", payload);
    }
  }
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
    // Signed out (or the session expired): go to the login page and come back afterwards.
    if (res.status === 401 && err.error === "unauthorized" && location.pathname !== "/login") {
      location.assign(`/login?next=${encodeURIComponent(location.pathname + location.search)}`);
    }
    throw new ApiError(res.status, err.error ?? "unknown", err.message ?? res.statusText);
  }
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

export const api = {
  tracks: () => request<TrackSummary[]>("GET", "/tracks"),
  aiStatus: () => request<AiStatus>("GET", "/ai/status"),
  aiHistory: (id: string) => request<AiMessage[]>("GET", `/ai/chat/${id}`),
  aiClear: (id: string) => request<void>("DELETE", `/ai/chat/${id}`),
  aiPatterns: () => request<PatternsReport | null>("GET", "/ai/patterns"),
  aiRefreshPatterns: () => request<PatternsReport>("POST", "/ai/patterns"),
  activity: (sections: readonly Section[]) => request<Activity>("GET", `/activity?sections=${sections.join(",")}`),
  track: (slug: string) => request<TrackDetail>("GET", `/tracks/${slug}`),
  problem: (id: string) => request<ProblemDetail>("GET", `/problems/${id}`),
  saveDraft: (id: string, code: string) => request<void>("PUT", `/problems/${id}/draft`, { code }),
  reset: (id: string) => request<ProblemDetail>("DELETE", `/problems/${id}/draft`),
  run: (id: string, code: string) => request<RunOutcome>("POST", `/problems/${id}/run`, { code }),
  saveScratch: (id: string, code: string) => request<void>("PUT", `/problems/${id}/scratch`, { code }),
  runScratch: (id: string, lib: string, main: string) => request<ScratchResult>("POST", `/problems/${id}/scratch/run`, { lib, main }),
  submit: (id: string, code: string) => request<RunOutcome>("POST", `/problems/${id}/submit`, { code }),
  revealHint: (id: string) => request<ProblemDetail>("POST", `/problems/${id}/hints`),
  revealSolution: (id: string) => request<ProblemDetail>("POST", `/problems/${id}/solution`),
  session: () => request<{ required: boolean; authenticated: boolean }>("GET", "/auth/session"),
  login: (passphrase: string) => request<void>("POST", "/auth/login", { passphrase }),
  logout: () => request<void>("POST", "/auth/logout"),
  settings: () => request<Settings>("GET", "/settings"),
  saveEditor: (editor: EditorSettings) => request<EditorSettings>("PUT", "/settings/editor", editor),
  format: (code: string) => request<{ code: string }>("POST", "/format", { code }).then((r) => r.code),
  saveAppearance: (appearance: AppearanceSettings) => request<AppearanceSettings>("PUT", "/settings/appearance", appearance),
  progress: () => request<ProgressOverview>("GET", "/progress"),
  stats: () => request<ProgressStats>("GET", "/stats"),
  reviews: () => request<ReviewsView>("GET", "/reviews"),
  resolve: (id: string) => request<ProblemDetail>("POST", `/problems/${id}/resolve`),
  focus: (id: string, seconds: number) => request<void>("POST", `/problems/${id}/focus`, { seconds }),
};
