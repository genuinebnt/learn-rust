use axum::Json;
use axum::extract::ws::WebSocketUpgrade;
use axum::extract::{Path, State};
use axum::http::StatusCode;
use axum::response::Response;
use serde_json::{Value, json};

use anneal_content::{Problem, Status, Track};
use anneal_runner::{RunStatus, Submission};

use crate::AppState;
use crate::error::{ApiError, ApiResult};
use crate::lsp::{self, SessionFiles};
use crate::store;
use crate::views::{self, CodeBody, ProblemDetail, RunOutcome, TrackDetail, TrackSummary};

/// Longest editor buffer accepted, in bytes.
const MAX_CODE: usize = 256 * 1024;

pub async fn health(State(s): State<AppState>) -> Json<Value> {
    let problems: usize = s.catalog.tracks.iter().map(|t| t.problems.len()).sum();
    Json(json!({ "ok": true, "tracks": s.catalog.tracks.len(), "problems": problems }))
}

pub async fn tracks(State(s): State<AppState>) -> ApiResult<Json<Vec<TrackSummary>>> {
    let progress = store::progress(&s.db).await?;
    Ok(Json(
        s.catalog
            .tracks
            .iter()
            .map(|t| views::track_summary(t, &progress))
            .collect(),
    ))
}

pub async fn track(
    State(s): State<AppState>,
    Path(slug): Path<String>,
) -> ApiResult<Json<TrackDetail>> {
    let t = s
        .catalog
        .track(&slug)
        .ok_or_else(|| ApiError::NotFound(format!("track {slug}")))?;
    let progress = store::progress(&s.db).await?;
    Ok(Json(views::track_detail(t, &progress)))
}

fn find<'a>(s: &'a AppState, id: &str) -> ApiResult<(&'a Track, &'a Problem)> {
    s.catalog
        .problem(id)
        .ok_or_else(|| ApiError::NotFound(format!("problem {id}")))
}

async fn detail(s: &AppState, id: &str) -> ApiResult<ProblemDetail> {
    let (t, p) = find(s, id)?;
    let attempt = store::latest_attempt(&s.db, id).await?;
    let runs = match &attempt {
        Some(a) => store::runs(&s.db, a.id).await?,
        None => Vec::new(),
    };
    let draft = store::draft(&s.db, id).await?;
    Ok(views::problem_detail(t, p, attempt.as_ref(), draft, runs))
}

pub async fn problem(
    State(s): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Json<ProblemDetail>> {
    Ok(Json(detail(&s, &id).await?))
}

fn check_code(code: &str) -> ApiResult<()> {
    if code.len() > MAX_CODE {
        return Err(ApiError::BadRequest(format!(
            "code is {} bytes; the limit is {MAX_CODE}",
            code.len()
        )));
    }
    Ok(())
}

pub async fn save_draft(
    State(s): State<AppState>,
    Path(id): Path<String>,
    Json(body): Json<CodeBody>,
) -> ApiResult<StatusCode> {
    find(&s, &id)?;
    check_code(&body.code)?;
    store::save_draft(&s.db, &id, &body.code).await?;
    Ok(StatusCode::NO_CONTENT)
}

/// Reset: drop the draft so the editor goes back to the starter.
pub async fn reset(
    State(s): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Json<ProblemDetail>> {
    find(&s, &id)?;
    store::delete_draft(&s.db, &id).await?;
    Ok(Json(detail(&s, &id).await?))
}

pub async fn run(
    State(s): State<AppState>,
    Path(id): Path<String>,
    Json(body): Json<CodeBody>,
) -> ApiResult<Json<RunOutcome>> {
    execute(&s, &id, &body.code, false).await.map(Json)
}

pub async fn submit(
    State(s): State<AppState>,
    Path(id): Path<String>,
    Json(body): Json<CodeBody>,
) -> ApiResult<Json<RunOutcome>> {
    execute(&s, &id, &body.code, true).await.map(Json)
}

/// Run: visible tests only. Submit: visible and hidden; all passing, with no rule broken, solves the problem.
async fn execute(s: &AppState, id: &str, code: &str, with_hidden: bool) -> ApiResult<RunOutcome> {
    let (_, p) = find(s, id)?;
    check_code(code)?;
    if p.meta.status != Status::Ready {
        return Err(ApiError::NotReady(id.to_owned()));
    }
    let visible = p.files.visible_tests.as_deref().unwrap_or_default();
    let hidden = with_hidden.then(|| p.files.hidden_tests.as_deref().unwrap_or_default());
    store::save_draft(&s.db, id, code).await?;
    let result = s
        .runner
        .run(
            id,
            &Submission {
                lib_rs: code,
                visible_tests: visible,
                hidden_tests: hidden,
            },
        )
        .await?;

    // Fix-this rules are checked against the source; the tests still run so you see both.
    let violations = match (&p.meta.rules, &p.files.starter) {
        (Some(rules), Some(starter)) => anneal_rules::check(code, starter, rules),
        _ => Vec::new(),
    };

    let mut attempt = store::current_attempt(&s.db, id).await?;
    let kind = if with_hidden { "submit" } else { "run" };
    let row = store::insert_run(&s.db, attempt.id, id, kind, code, &result, &violations).await?;
    if with_hidden && result.status == RunStatus::Passed && violations.is_empty() {
        attempt = store::mark_solved(&s.db, attempt.id).await?;
    }
    Ok(RunOutcome {
        run: row.into(),
        attempt: Some(&attempt).into(),
        solution: views::solution_view(p, Some(&attempt)),
    })
}

pub async fn reveal_hint(
    State(s): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Json<ProblemDetail>> {
    let (_, p) = find(&s, &id)?;
    if p.meta.hints.is_empty() {
        return Err(ApiError::BadRequest(format!("{id} has no hints")));
    }
    let attempt = store::current_attempt(&s.db, &id).await?;
    if (attempt.hints_revealed as usize) < p.meta.hints.len() {
        store::reveal_hint(&s.db, attempt.id, p.meta.hints.len() as i32).await?;
    }
    Ok(Json(detail(&s, &id).await?))
}

pub async fn reveal_solution(
    State(s): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Json<ProblemDetail>> {
    let (_, p) = find(&s, &id)?;
    if p.files.solution.is_none() {
        return Err(ApiError::NotReady(id));
    }
    let attempt = store::current_attempt(&s.db, &id).await?;
    store::reveal_solution(&s.db, attempt.id).await?;
    Ok(Json(detail(&s, &id).await?))
}

/// Upgrades to a WebSocket running rust-analyzer on this problem. See [`crate::lsp`].
pub async fn lsp(
    ws: WebSocketUpgrade,
    State(s): State<AppState>,
    Path(id): Path<String>,
) -> ApiResult<Response> {
    let (_, p) = find(&s, &id)?;
    let starter = p
        .files
        .starter
        .clone()
        .ok_or_else(|| ApiError::NotReady(id.clone()))?;
    let lib_rs = store::draft(&s.db, &id).await?.unwrap_or(starter);
    let visible_tests = p.files.visible_tests.clone().unwrap_or_default();
    let permit = s.lsp.slots.clone().try_acquire_owned().map_err(|_| {
        ApiError::Busy(
            "rust-analyzer is already running for 3 editors; close one and try again".into(),
        )
    })?;
    let cfg = s.lsp.clone();
    Ok(ws.on_upgrade(move |socket| async move {
        if let Err(e) = lsp::session(
            socket,
            cfg,
            SessionFiles {
                lib_rs,
                visible_tests,
            },
        )
        .await
        {
            tracing::warn!(error = %e, problem = %id, "rust-analyzer session ended with an error");
        }
        drop(permit);
    }))
}
