//! Progress data: attempts, runs and drafts.

use std::collections::HashMap;

use anneal_rules::Violation;
use anneal_runner::RunResult;
use chrono::{DateTime, Utc};
use sqlx::PgPool;
use sqlx::types::Json;

#[derive(Debug, Clone, sqlx::FromRow)]
pub struct Attempt {
    pub id: i64,
    pub started_at: DateTime<Utc>,
    pub solved_at: Option<DateTime<Utc>>,
    pub hints_revealed: i32,
    pub solution_revealed: bool,
    pub assisted: bool,
    /// `practice` (first time through) or `resolve` (a scheduled review).
    pub kind: String,
}

#[derive(Debug, Clone, sqlx::FromRow)]
pub struct RunRow {
    pub id: i64,
    pub kind: String,
    pub code: String,
    pub result: Json<RunResult>,
    pub violations: Json<Vec<Violation>>,
    pub created_at: DateTime<Utc>,
}

const ATTEMPT_COLS: &str = "id, started_at, solved_at, hints_revealed, solution_revealed, assisted, kind";

pub async fn latest_attempt(db: &PgPool, problem_id: &str) -> sqlx::Result<Option<Attempt>> {
    sqlx::query_as(&format!("SELECT {ATTEMPT_COLS} FROM attempts WHERE problem_id = $1 ORDER BY started_at DESC, id DESC LIMIT 1"))
        .bind(problem_id)
        .fetch_optional(db)
        .await
}

/// The latest attempt, or a new one if the problem was never attempted.
pub async fn current_attempt(db: &PgPool, problem_id: &str) -> sqlx::Result<Attempt> {
    if let Some(a) = latest_attempt(db, problem_id).await? {
        return Ok(a);
    }
    sqlx::query_as(&format!(
        "INSERT INTO attempts (problem_id) VALUES ($1) RETURNING {ATTEMPT_COLS}"
    ))
    .bind(problem_id)
    .fetch_one(db)
    .await
}

/// Reveals one more hint, up to `max`. Hints opened before solving make the attempt assisted.
pub async fn reveal_hint(db: &PgPool, attempt_id: i64, max: i32) -> sqlx::Result<Attempt> {
    sqlx::query_as(&format!(
        "UPDATE attempts SET hints_revealed = LEAST(hints_revealed + 1, $2), assisted = assisted OR solved_at IS NULL
         WHERE id = $1 RETURNING {ATTEMPT_COLS}"
    ))
    .bind(attempt_id)
    .bind(max)
    .fetch_one(db)
    .await
}

/// "Reveal anyway": assisted unless the problem was already solved.
pub async fn reveal_solution(db: &PgPool, attempt_id: i64) -> sqlx::Result<Attempt> {
    sqlx::query_as(&format!(
        "UPDATE attempts SET solution_revealed = true, assisted = assisted OR solved_at IS NULL
         WHERE id = $1 RETURNING {ATTEMPT_COLS}"
    ))
    .bind(attempt_id)
    .fetch_one(db)
    .await
}

pub async fn mark_solved(db: &PgPool, attempt_id: i64) -> sqlx::Result<Attempt> {
    sqlx::query_as(&format!("UPDATE attempts SET solved_at = COALESCE(solved_at, now()) WHERE id = $1 RETURNING {ATTEMPT_COLS}"))
        .bind(attempt_id)
        .fetch_one(db)
        .await
}

pub async fn insert_run(
    db: &PgPool,
    attempt_id: i64,
    problem_id: &str,
    kind: &str,
    code: &str,
    result: &RunResult,
    violations: &[Violation],
) -> sqlx::Result<RunRow> {
    let status = serde_json::to_value(result.status)
        .ok()
        .and_then(|v| v.as_str().map(str::to_owned))
        .unwrap_or_default();
    sqlx::query_as(
        "INSERT INTO runs (attempt_id, problem_id, kind, code, status, passed, total, result, violations)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
         RETURNING id, kind, code, result, violations, created_at",
    )
    .bind(attempt_id)
    .bind(problem_id)
    .bind(kind)
    .bind(code)
    .bind(status)
    .bind(result.passed as i32)
    .bind(result.total as i32)
    .bind(Json(result))
    .bind(Json(violations))
    .fetch_one(db)
    .await
}

/// Runs in an attempt, oldest first.
pub async fn runs(db: &PgPool, attempt_id: i64) -> sqlx::Result<Vec<RunRow>> {
    sqlx::query_as(
        "SELECT id, kind, code, result, violations, created_at FROM runs WHERE attempt_id = $1 ORDER BY id",
    )
    .bind(attempt_id)
    .fetch_all(db)
    .await
}

pub async fn draft(db: &PgPool, problem_id: &str) -> sqlx::Result<Option<String>> {
    sqlx::query_scalar("SELECT code FROM drafts WHERE problem_id = $1")
        .bind(problem_id)
        .fetch_optional(db)
        .await
}

pub async fn save_draft(db: &PgPool, problem_id: &str, code: &str) -> sqlx::Result<()> {
    sqlx::query(
        "INSERT INTO drafts (problem_id, code) VALUES ($1, $2)
         ON CONFLICT (problem_id) DO UPDATE SET code = EXCLUDED.code, updated_at = now()",
    )
    .bind(problem_id)
    .bind(code)
    .execute(db)
    .await?;
    Ok(())
}

pub async fn delete_draft(db: &PgPool, problem_id: &str) -> sqlx::Result<()> {
    sqlx::query("DELETE FROM drafts WHERE problem_id = $1")
        .bind(problem_id)
        .execute(db)
        .await?;
    Ok(())
}

#[derive(Debug, Clone, Copy)]
pub struct ProgressRow {
    pub solved: bool,
    pub assisted: bool,
    /// Readiness multiplier from an overdue review (1.0 when not overdue); see [`crate::reviews::decay`].
    pub decay: f64,
}

/// Per problem: the latest solved attempt if there is one (a re-solve in progress keeps the earlier
/// credit), otherwise the latest attempt.
pub async fn progress(db: &PgPool) -> sqlx::Result<HashMap<String, ProgressRow>> {
    let rows: Vec<(String, bool, bool, Option<DateTime<Utc>>)> = sqlx::query_as(
        "SELECT DISTINCT ON (a.problem_id) a.problem_id, a.solved_at IS NOT NULL, a.assisted, r.due_at
         FROM attempts a LEFT JOIN reviews r ON r.problem_id = a.problem_id
         ORDER BY a.problem_id, (a.solved_at IS NOT NULL) DESC, a.started_at DESC, a.id DESC",
    )
    .fetch_all(db)
    .await?;
    let now = Utc::now();
    Ok(rows
        .into_iter()
        .map(|(id, solved, assisted, due)| {
            let decay = due.map_or(1.0, |d| crate::reviews::decay(d, now));
            (id, ProgressRow { solved, assisted, decay })
        })
        .collect())
}

/// Starts a scheduled re-solve: a new attempt (hints locked again) and the editor back to the starter.
pub async fn start_resolve(db: &PgPool, problem_id: &str) -> sqlx::Result<()> {
    let mut tx = db.begin().await?;
    sqlx::query("INSERT INTO attempts (problem_id, kind) VALUES ($1, 'resolve')")
        .bind(problem_id)
        .execute(&mut *tx)
        .await?;
    sqlx::query("DELETE FROM drafts WHERE problem_id = $1").bind(problem_id).execute(&mut *tx).await?;
    tx.commit().await
}

#[derive(Debug, Clone, sqlx::FromRow)]
pub struct ReviewRow {
    pub problem_id: String,
    pub step: i32,
    pub due_at: DateTime<Utc>,
    pub last_result: String,
    pub history: Json<Vec<serde_json::Value>>,
}

pub async fn reviews(db: &PgPool) -> sqlx::Result<Vec<ReviewRow>> {
    sqlx::query_as("SELECT problem_id, step, due_at, last_result, history FROM reviews ORDER BY due_at")
        .fetch_all(db)
        .await
}

/// Schedules the next review after a solve.
pub async fn record_solve(db: &PgPool, problem_id: &str, outcome: crate::reviews::Outcome, resolve: bool) -> sqlx::Result<()> {
    let prev: Option<i32> = sqlx::query_scalar("SELECT step FROM reviews WHERE problem_id = $1")
        .bind(problem_id)
        .fetch_optional(db)
        .await?;
    let (step, days) = crate::reviews::next(prev, outcome);
    let entry = serde_json::json!({ "at": Utc::now(), "result": outcome.as_str(), "resolve": resolve, "step": step });
    sqlx::query(
        "INSERT INTO reviews (problem_id, step, due_at, last_result, history)
         VALUES ($1, $2, now() + make_interval(days => $3), $4, jsonb_build_array($5::jsonb))
         ON CONFLICT (problem_id) DO UPDATE SET step = EXCLUDED.step, due_at = EXCLUDED.due_at,
             last_result = EXCLUDED.last_result, history = reviews.history || $5::jsonb, updated_at = now()",
    )
    .bind(problem_id)
    .bind(step)
    .bind(days as i32)
    .bind(outcome.as_str())
    .bind(Json(entry))
    .execute(db)
    .await?;
    Ok(())
}

/// Adds active-editing seconds for a problem on a (local) day.
pub async fn add_focus(db: &PgPool, day: chrono::NaiveDate, problem_id: &str, seconds: i32) -> sqlx::Result<()> {
    sqlx::query(
        "INSERT INTO focus_time (day, problem_id, seconds) VALUES ($1, $2, $3)
         ON CONFLICT (day, problem_id) DO UPDATE SET seconds = focus_time.seconds + EXCLUDED.seconds",
    )
    .bind(day)
    .bind(problem_id)
    .bind(seconds)
    .execute(db)
    .await?;
    Ok(())
}

pub async fn focus(db: &PgPool) -> sqlx::Result<Vec<(chrono::NaiveDate, String, i32)>> {
    sqlx::query_as("SELECT day, problem_id, seconds FROM focus_time").fetch_all(db).await
}

/// Every run, oldest first, with just what the stats need.
#[derive(Debug, Clone, sqlx::FromRow)]
pub struct RunStat {
    pub attempt_id: i64,
    pub problem_id: String,
    pub status: String,
    pub diagnostics: Json<Vec<anneal_runner::Diagnostic>>,
    pub violations: Json<Vec<Violation>>,
    pub created_at: DateTime<Utc>,
}

pub async fn run_stats(db: &PgPool) -> sqlx::Result<Vec<RunStat>> {
    sqlx::query_as(
        "SELECT attempt_id, problem_id, status, result -> 'diagnostics' AS diagnostics, violations, created_at
         FROM runs ORDER BY id",
    )
    .fetch_all(db)
    .await
}

/// One attempt with its run count and latest activity, for the activity rail.
#[derive(Debug, Clone, sqlx::FromRow)]
pub struct ActivityRow {
    pub attempt_id: i64,
    pub kind: String,
    pub problem_id: String,
    pub started_at: DateTime<Utc>,
    pub solved_at: Option<DateTime<Utc>>,
    pub assisted: bool,
    pub hints_revealed: i32,
    pub solution_revealed: bool,
    pub runs: i64,
    pub last_at: DateTime<Utc>,
}

/// Every attempt, most recently active first.
pub async fn activity(db: &PgPool) -> sqlx::Result<Vec<ActivityRow>> {
    sqlx::query_as(
        "SELECT a.id AS attempt_id, a.kind, a.problem_id, a.started_at, a.solved_at, a.assisted, a.hints_revealed, a.solution_revealed,
                count(r.id) AS runs,
                GREATEST(a.started_at, COALESCE(a.solved_at, a.started_at), COALESCE(max(r.created_at), a.started_at)) AS last_at
         FROM attempts a LEFT JOIN runs r ON r.attempt_id = a.id
         GROUP BY a.id
         ORDER BY last_at DESC, a.id DESC",
    )
    .fetch_all(db)
    .await
}

pub async fn scratch(db: &PgPool, problem_id: &str) -> sqlx::Result<Option<String>> {
    sqlx::query_scalar("SELECT code FROM scratch WHERE problem_id = $1").bind(problem_id).fetch_optional(db).await
}

pub async fn save_scratch(db: &PgPool, problem_id: &str, code: &str) -> sqlx::Result<()> {
    sqlx::query(
        "INSERT INTO scratch (problem_id, code) VALUES ($1, $2)
         ON CONFLICT (problem_id) DO UPDATE SET code = EXCLUDED.code, updated_at = now()",
    )
    .bind(problem_id)
    .bind(code)
    .execute(db)
    .await?;
    Ok(())
}

/// Whether any attempt at the problem has been solved; hidden tests open up after that.
pub async fn ever_solved(db: &PgPool, problem_id: &str) -> sqlx::Result<bool> {
    sqlx::query_scalar("SELECT EXISTS (SELECT 1 FROM attempts WHERE problem_id = $1 AND solved_at IS NOT NULL)")
        .bind(problem_id)
        .fetch_one(db)
        .await
}

// ---------------------------------------------------------------- AI assistant

/// One attempt you've run code in, summarised for the assistant's embeddings.
#[derive(sqlx::FromRow)]
pub struct AttemptSummary {
    pub attempt_id: i64,
    pub problem_id: String,
    pub solved: bool,
    pub assisted: bool,
    /// Distinct error and lint codes across its runs, e.g. `E0502`, `clippy::needless_range_loop`.
    pub errors: Vec<String>,
    pub last_code: String,
}

pub async fn attempt_summaries(db: &PgPool) -> sqlx::Result<Vec<AttemptSummary>> {
    sqlx::query_as(
        "SELECT a.id AS attempt_id, a.problem_id, a.solved_at IS NOT NULL AS solved, a.assisted,
                COALESCE((SELECT array_agg(DISTINCT d->>'code')
                          FROM runs r, jsonb_array_elements(r.result->'diagnostics') d
                          WHERE r.attempt_id = a.id AND d->>'code' IS NOT NULL), '{}') AS errors,
                (SELECT code FROM runs r WHERE r.attempt_id = a.id ORDER BY r.id DESC LIMIT 1) AS last_code
         FROM attempts a
         WHERE EXISTS (SELECT 1 FROM runs r WHERE r.attempt_id = a.id)
         ORDER BY a.id",
    )
    .fetch_all(db)
    .await
}

/// The latest run of the current attempt at a problem, if any.
pub async fn latest_run(db: &PgPool, problem_id: &str) -> sqlx::Result<Option<RunRow>> {
    let Some(a) = latest_attempt(db, problem_id).await? else { return Ok(None) };
    Ok(runs(db, a.id).await?.pop())
}

/// Marks an attempt assisted: help before a solve counts like a hint.
pub async fn mark_assisted(db: &PgPool, attempt_id: i64) -> sqlx::Result<()> {
    sqlx::query("UPDATE attempts SET assisted = true WHERE id = $1 AND solved_at IS NULL")
        .bind(attempt_id)
        .execute(db)
        .await?;
    Ok(())
}

#[derive(Debug, Clone, serde::Serialize, sqlx::FromRow)]
pub struct AiMessage {
    pub id: i64,
    pub role: String,
    pub content: String,
    pub action: Option<String>,
    pub sources: Json<serde_json::Value>,
    pub created_at: DateTime<Utc>,
}

pub async fn ai_messages(db: &PgPool, problem_id: &str) -> sqlx::Result<Vec<AiMessage>> {
    sqlx::query_as("SELECT id, role, content, action, sources, created_at FROM ai_messages WHERE problem_id = $1 ORDER BY id")
        .bind(problem_id)
        .fetch_all(db)
        .await
}

pub async fn add_ai_message(
    db: &PgPool,
    problem_id: &str,
    role: &str,
    content: &str,
    action: Option<&str>,
    sources: &serde_json::Value,
) -> sqlx::Result<()> {
    sqlx::query("INSERT INTO ai_messages (problem_id, role, content, action, sources) VALUES ($1, $2, $3, $4, $5)")
        .bind(problem_id)
        .bind(role)
        .bind(content)
        .bind(action)
        .bind(Json(sources))
        .execute(db)
        .await?;
    Ok(())
}

pub async fn clear_ai_messages(db: &PgPool, problem_id: &str) -> sqlx::Result<()> {
    sqlx::query("DELETE FROM ai_messages WHERE problem_id = $1").bind(problem_id).execute(db).await?;
    Ok(())
}

pub async fn ai_report(db: &PgPool, kind: &str) -> sqlx::Result<Option<(serde_json::Value, String, DateTime<Utc>)>> {
    let row: Option<(Json<serde_json::Value>, String, DateTime<Utc>)> =
        sqlx::query_as("SELECT content, model, created_at FROM ai_reports WHERE kind = $1").bind(kind).fetch_optional(db).await?;
    Ok(row.map(|(c, m, t)| (c.0, m, t)))
}

pub async fn save_ai_report(db: &PgPool, kind: &str, content: &serde_json::Value, model: &str) -> sqlx::Result<()> {
    sqlx::query(
        "INSERT INTO ai_reports (kind, content, model) VALUES ($1, $2, $3)
         ON CONFLICT (kind) DO UPDATE SET content = EXCLUDED.content, model = EXCLUDED.model, created_at = now()",
    )
    .bind(kind)
    .bind(Json(content))
    .bind(model)
    .execute(db)
    .await?;
    Ok(())
}
