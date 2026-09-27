//! JSON shapes the web app reads. Kept separate from the content and DB types so
//! what reaches the browser is decided in one place (hidden tests, locked solutions).

use std::collections::HashMap;

use anneal_content::model::{Example, Hint, SolutionNotes};
use anneal_content::{Band, Mode, Problem, Rules, Section, Status, Tier, Track};
use anneal_rules::Violation;
use anneal_runner::{Check, Diagnostic, Outcome, RunResult, RunStatus, Suite, TestOutcome};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use crate::store::{Attempt, ProgressRow, RunRow};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Progress {
    NotStarted,
    Started,
    Solved,
    Assisted,
}

impl Progress {
    fn of(row: Option<&ProgressRow>) -> Self {
        match row {
            None => Progress::NotStarted,
            Some(r) if !r.solved => Progress::Started,
            Some(r) if r.assisted => Progress::Assisted,
            Some(_) => Progress::Solved,
        }
    }

    fn solved(self) -> bool {
        matches!(self, Progress::Solved | Progress::Assisted)
    }
}

#[derive(Debug, Serialize)]
pub struct TrackSummary {
    pub code: String,
    pub slug: String,
    pub name: String,
    pub section: Section,
    pub tier: Tier,
    pub order: u32,
    pub summary: String,
    pub stages: Vec<StageView>,
    pub total: usize,
    pub ready: usize,
    pub solved: usize,
}

#[derive(Debug, Serialize)]
pub struct StageView {
    pub slug: String,
    pub name: String,
    pub band: Band,
    pub total: usize,
    pub ready: usize,
    pub solved: usize,
}

#[derive(Debug, Serialize)]
pub struct TrackDetail {
    #[serde(flatten)]
    pub summary: TrackSummary,
    pub problems: Vec<ProblemSummary>,
}

#[derive(Debug, Serialize)]
pub struct ProblemSummary {
    pub id: String,
    pub slug: String,
    pub title: String,
    pub mode: Mode,
    pub level: Band,
    pub stage: String,
    pub order: u32,
    pub status: Status,
    pub tags: Vec<String>,
    pub progress: Progress,
}

pub fn track_summary(t: &Track, progress: &HashMap<String, ProgressRow>) -> TrackSummary {
    let state = |p: &Problem| Progress::of(progress.get(&p.id));
    let stages = t
        .stages
        .iter()
        .map(|s| {
            let ps: Vec<&Problem> = t
                .problems
                .iter()
                .filter(|p| p.meta.stage == s.slug)
                .collect();
            StageView {
                slug: s.slug.clone(),
                name: s.name.clone(),
                band: s.band,
                total: ps.len(),
                ready: ps.iter().filter(|p| p.meta.status == Status::Ready).count(),
                solved: ps.iter().filter(|p| state(p).solved()).count(),
            }
        })
        .collect();
    TrackSummary {
        code: t.code.clone(),
        slug: t.slug.clone(),
        name: t.name.clone(),
        section: t.section,
        tier: t.tier,
        order: t.order,
        summary: t.summary.clone(),
        stages,
        total: t.problems.len(),
        ready: t
            .problems
            .iter()
            .filter(|p| p.meta.status == Status::Ready)
            .count(),
        solved: t.problems.iter().filter(|p| state(p).solved()).count(),
    }
}

pub fn track_detail(t: &Track, progress: &HashMap<String, ProgressRow>) -> TrackDetail {
    TrackDetail {
        summary: track_summary(t, progress),
        problems: t
            .problems
            .iter()
            .map(|p| ProblemSummary {
                id: p.id.clone(),
                slug: p.meta.slug.clone(),
                title: p.meta.title.clone(),
                mode: p.meta.mode,
                level: p.meta.level,
                stage: p.meta.stage.clone(),
                order: p.meta.order,
                status: p.meta.status,
                tags: p.meta.tags.clone(),
                progress: Progress::of(progress.get(&p.id)),
            })
            .collect(),
    }
}

#[derive(Debug, Serialize)]
pub struct ProblemDetail {
    pub id: String,
    pub slug: String,
    pub title: String,
    pub mode: Mode,
    pub level: Band,
    pub status: Status,
    pub track: TrackRef,
    pub stage: StageRef,
    /// 1-based position in the track, and the track's size.
    pub position: usize,
    pub count: usize,
    pub prev: Option<String>,
    pub next: Option<String>,
    pub statement: String,
    pub tags: Vec<String>,
    pub teaches: Vec<String>,
    pub constraints: Vec<String>,
    pub examples: Vec<Example>,
    pub follow_up: Option<String>,
    pub related: Vec<String>,
    pub rules: Option<Rules>,
    pub starter: String,
    /// The autosaved buffer, if it differs from the starter.
    pub draft: Option<String>,
    pub visible_tests: String,
    pub hints: HintsView,
    pub solution: SolutionView,
    pub attempt: AttemptView,
    /// Runs in the current attempt, oldest first.
    pub runs: Vec<RunView>,
}

#[derive(Debug, Serialize)]
pub struct TrackRef {
    pub code: String,
    pub slug: String,
    pub name: String,
    pub section: Section,
}

#[derive(Debug, Serialize)]
pub struct StageRef {
    pub slug: String,
    pub name: String,
    pub band: Band,
    /// 1-based stage number in the track.
    pub number: usize,
    /// 1-based position of this problem in the stage, and the stage's size.
    pub position: usize,
    pub count: usize,
}

#[derive(Debug, Serialize)]
pub struct HintsView {
    pub total: usize,
    pub revealed: Vec<Hint>,
    /// Kinds of the hints still hidden, e.g. "edge case", so the UI can label them.
    pub locked: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct SolutionView {
    pub unlocked: bool,
    /// Present only when unlocked.
    pub code: Option<String>,
    pub notes: Option<SolutionNotes>,
}

#[derive(Debug, Default, Serialize)]
pub struct AttemptView {
    pub started: bool,
    pub started_at: Option<DateTime<Utc>>,
    pub solved: bool,
    pub assisted: bool,
    pub hints_revealed: usize,
    pub solution_revealed: bool,
}

impl From<Option<&Attempt>> for AttemptView {
    fn from(a: Option<&Attempt>) -> Self {
        match a {
            None => AttemptView::default(),
            Some(a) => AttemptView {
                started: true,
                started_at: Some(a.started_at),
                solved: a.solved_at.is_some(),
                assisted: a.assisted,
                hints_revealed: a.hints_revealed.max(0) as usize,
                solution_revealed: a.solution_revealed,
            },
        }
    }
}

#[derive(Debug, Serialize)]
pub struct RunView {
    pub id: i64,
    pub kind: String,
    pub created_at: DateTime<Utc>,
    pub code: String,
    pub status: RunStatus,
    pub passed: usize,
    pub total: usize,
    pub duration_ms: u64,
    pub diagnostics: Vec<Diagnostic>,
    pub tests: Vec<TestOutcome>,
    /// Fix-this rules this run broke. Any violation keeps a submit from solving the problem.
    pub violations: Vec<Violation>,
}

impl From<RunRow> for RunView {
    fn from(row: RunRow) -> Self {
        let RunResult {
            status,
            diagnostics,
            tests,
            passed,
            total,
            duration_ms,
        } = row.result.0;
        RunView {
            id: row.id,
            kind: row.kind,
            created_at: row.created_at,
            code: row.code,
            status,
            passed,
            total,
            duration_ms,
            diagnostics,
            tests: tests.into_iter().map(redact).collect(),
            violations: row.violations.0,
        }
    }
}

/// Hidden tests report only pass or fail: no input, expected value, output or panic text.
fn redact(t: TestOutcome) -> TestOutcome {
    if t.suite != Suite::Hidden {
        return t;
    }
    let failed = matches!(t.outcome, Outcome::Failed | Outcome::TimedOut);
    TestOutcome {
        check: failed.then(|| Check {
            input: "withheld".into(),
            expected: "withheld".into(),
            got: "wrong answer".into(),
        }),
        panic: None,
        stdout: String::new(),
        ..t
    }
}

pub fn problem_detail(
    track: &Track,
    p: &Problem,
    attempt: Option<&Attempt>,
    draft: Option<String>,
    runs: Vec<RunRow>,
) -> ProblemDetail {
    let idx = track
        .problems
        .iter()
        .position(|q| q.id == p.id)
        .unwrap_or(0);
    let stage_def = track.stage(&p.meta.stage);
    let in_stage: Vec<&Problem> = track
        .problems
        .iter()
        .filter(|q| q.meta.stage == p.meta.stage)
        .collect();
    let starter = p.files.starter.clone().unwrap_or_default();
    let revealed = attempt
        .map_or(0, |a| a.hints_revealed.max(0) as usize)
        .min(p.meta.hints.len());
    ProblemDetail {
        id: p.id.clone(),
        slug: p.meta.slug.clone(),
        title: p.meta.title.clone(),
        mode: p.meta.mode,
        level: p.meta.level,
        status: p.meta.status,
        track: TrackRef {
            code: track.code.clone(),
            slug: track.slug.clone(),
            name: track.name.clone(),
            section: track.section,
        },
        stage: StageRef {
            slug: p.meta.stage.clone(),
            name: stage_def.map(|s| s.name.clone()).unwrap_or_default(),
            band: stage_def.map_or(p.meta.level, |s| s.band),
            number: track
                .stages
                .iter()
                .position(|s| s.slug == p.meta.stage)
                .map_or(0, |i| i + 1),
            position: in_stage
                .iter()
                .position(|q| q.id == p.id)
                .map_or(0, |i| i + 1),
            count: in_stage.len(),
        },
        position: idx + 1,
        count: track.problems.len(),
        prev: idx.checked_sub(1).map(|i| track.problems[i].id.clone()),
        next: track.problems.get(idx + 1).map(|q| q.id.clone()),
        statement: p.files.statement.clone().unwrap_or_default(),
        tags: p.meta.tags.clone(),
        teaches: p.meta.teaches.clone(),
        constraints: p.meta.constraints.clone(),
        examples: p.meta.examples.clone(),
        follow_up: p.meta.follow_up.clone(),
        related: p.meta.related.clone(),
        rules: p.meta.rules.clone(),
        draft: draft.filter(|d| *d != starter),
        starter,
        visible_tests: p.files.visible_tests.clone().unwrap_or_default(),
        hints: HintsView {
            total: p.meta.hints.len(),
            revealed: p.meta.hints[..revealed].to_vec(),
            locked: p.meta.hints[revealed..]
                .iter()
                .map(|h| h.kind.clone())
                .collect(),
        },
        solution: solution_view(p, attempt),
        attempt: attempt.into(),
        runs: runs.into_iter().map(RunView::from).collect(),
    }
}

/// The solution opens once the problem is solved, or after "Reveal anyway".
pub fn solution_view(p: &Problem, attempt: Option<&Attempt>) -> SolutionView {
    let unlocked = attempt.is_some_and(|a| a.solved_at.is_some() || a.solution_revealed);
    SolutionView {
        unlocked,
        code: unlocked.then(|| p.files.solution.clone()).flatten(),
        notes: if unlocked {
            p.meta.solution.clone()
        } else {
            None
        },
    }
}

#[derive(Debug, Deserialize)]
pub struct CodeBody {
    pub code: String,
}

/// What Run and Submit return: the run plus the state it changed.
#[derive(Debug, Serialize)]
pub struct RunOutcome {
    pub run: RunView,
    pub attempt: AttemptView,
    pub solution: SolutionView,
}
