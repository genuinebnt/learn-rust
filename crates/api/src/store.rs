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

const ATTEMPT_COLS: &str = "id, started_at, solved_at, hints_revealed, solution_revealed, assisted";

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
}

/// Latest attempt per problem.
pub async fn progress(db: &PgPool) -> sqlx::Result<HashMap<String, ProgressRow>> {
    let rows: Vec<(String, bool, bool)> = sqlx::query_as(
        "SELECT DISTINCT ON (problem_id) problem_id, solved_at IS NOT NULL, assisted
         FROM attempts ORDER BY problem_id, started_at DESC, id DESC",
    )
    .fetch_all(db)
    .await?;
    Ok(rows
        .into_iter()
        .map(|(id, solved, assisted)| (id, ProgressRow { solved, assisted }))
        .collect())
}
