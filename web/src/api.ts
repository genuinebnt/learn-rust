// Types mirror crates/api/src/views.rs and crates/runner/src/result.rs.

export type Band = "easy" | "medium" | "hard";
export type Mode = "write" | "fix" | "stage";
export type Section = "D" | "L" | "S" | "C" | "Y" | "F" | "P";
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

export type Language = "rust" | "python";

export interface ProblemDetail {
  id: string;
  slug: string;
  title: string;
  mode: Mode;
  /** What the editor and runner speak. */
  language: Language;
  /** Practice problems: the DSA problems that open it, and whether it's also a warm-up for them. */
  unlocked_by: { id: string; slug: string; title: string }[];
  warmup: boolean;
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

export type Grade = "again" | "hard" | "good" | "easy";
export type Weekday = "mon" | "tue" | "wed" | "thu" | "fri" | "sat" | "sun";

/** Review scheduling and the DSA plan (`settings.srs`). */
export interface SrsSettings {
  retention: number;
  /** Reviews each weekday can take. */
  capacity: Record<Weekday, number>;
  consolidate_on: Weekday | null;
  /** The weekdays a new problem is solved on; the other days are practice or rest. */
  new_days: Weekday[];
  new_per_day: number;
  target_date: string | null;
  goal: { list: "blind75" | "neetcode150" | "neetcode250" | "all"; free_only: boolean; extra: number; custom_left: number | null };
}

export interface Settings {
  editor: EditorSettings;
  appearance: AppearanceSettings;
  srs: SrsSettings;
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
  readiness_trend: { area: "dsa" | "rust"; points: (number | null)[] }[];
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

export interface DsaCompany {
  name: string;
  group: string;
  frequency: number;
  recent: boolean;
}

export interface DsaStanding {
  /** Solved at least once. */
  solved: boolean;
  assisted: boolean;
  last_grade: Grade | null;
  reps: number;
  lapses: number;
  last_review: string | null;
  due: string | null;
  retrievability: number | null;
}

export type DsaListName = "blind75" | "neetcode150" | "neetcode250" | "all";

export interface DsaProblem {
  id: string;
  slug: string;
  number: number;
  title: string;
  difficulty: Band;
  /** The pattern's track code, e.g. D7. */
  pattern: string;
  lists: DsaListName[];
  premium: boolean;
  tags: string[];
  companies: DsaCompany[];
  video: string | null;
  technique: string;
  role: "must_learn" | "practice";
  practice_of: string | null;
  order: number;
  /** A written lesson exists. */
  has_page: boolean;
  state: DsaStanding;
}

export interface DsaApproach {
  name: string;
  label: string;
  idea: string;
  code: string;
  time: string;
  space: string;
  note: string;
}

/** The written lesson for a problem. Text is markdown. */
export interface DsaPage {
  intuition: string;
  tips: string[];
  approaches: DsaApproach[];
}

export interface DsaPattern {
  code: string;
  slug: string;
  name: string;
  total: number;
  in_150: number;
  solved: number;
  /** Practice problems for the pattern: how many, how many are open, how many solved. */
  practice_total: number;
  practice_open: number;
  practice_solved: number;
}

export interface PracticeProblem {
  id: string;
  slug: string;
  title: string;
  level: Band;
  order: number;
  /** The first paragraph of the statement, markdown. */
  blurb: string;
  teaches: string[];
  warmup: boolean;
  ready: boolean;
  open: boolean;
  progress: Progress;
  unlocked_by: { id: string; slug: string; title: string }[];
  /** The ids in `unlocked_by` that have been logged already. */
  logged: string[];
}

export interface PracticeTrack {
  code: string;
  slug: string;
  name: string;
  summary: string;
  language: Language;
  problems: PracticeProblem[];
}

export interface DsaTechnique {
  id: string;
  pattern: string;
  name: string;
  must_learn: string;
  problems: number;
}

export interface DsaPace {
  remaining: number;
  solve_days_left: number;
  per_solve_day: number | null;
  per_week: number | null;
  finish_at_current: string | null;
  days_vs_target: number | null;
}

export interface DsaPlan {
  goal_total: number;
  goal_done: number;
  pace: DsaPace;
  /** The next problems in order, from `start`. */
  next_up: string[];
  start: string | null;
  solve_day: boolean;
  capacity: number;
  /** Today's reviews, most forgotten first. */
  review_ids: string[];
  due: number;
  overdue: number;
}

export interface DsaOverview {
  today: string;
  settings: SrsSettings;
  patterns: DsaPattern[];
  techniques: DsaTechnique[];
  company_groups: { name: string; companies: string[] }[];
  problems: DsaProblem[];
  plan: DsaPlan;
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
  dsa: () => request<DsaOverview>("GET", "/dsa"),
  dsaPage: (id: string) => request<DsaPage | null>("GET", `/dsa/problems/${id}/page`),
  practice: (pattern: string) => request<PracticeTrack[]>("GET", `/dsa/practice/${pattern}`),
  logDsa: (id: string, grade: Grade) => request<{ id: string; due: string; ideal_days: number }>("POST", `/dsa/problems/${id}/log`, { grade }),
  startDsa: (from: string) => request<{ start: string }>("POST", "/dsa/start", { from }),
  saveSrs: (srs: SrsSettings) => request<SrsSettings>("PUT", "/settings/srs", srs),
  focus: (id: string, seconds: number) => request<void>("POST", `/problems/${id}/focus`, { seconds }),
};
