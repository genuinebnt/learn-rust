//! The practice tracks (docs/DSA.md, decision 23): handwritten problems per NeetCode pattern, solved in anneal.
//!
//! A practice problem opens once any of the DSA problems it is `unlocked_by` has been logged, with any grade. One
//! marked `warmup` also opens while one of those problems is coming up next in the plan, so it can be done first.
//! Practice never touches spaced repetition: solving one schedules no review and earns no readiness.

use std::collections::{HashMap, HashSet};

use anneal_content::{Band, Language, Problem, Section, Status};
use axum::Json;
use axum::extract::{Path, State};
use serde::Serialize;

use crate::AppState;
use crate::dsa::next_up_ids;
use crate::error::{ApiError, ApiResult};
use crate::store::{self, ProgressRow};
use crate::views::{Progress, UnlockRef};

/// How many of the next problems count as "coming up" for warm-ups.
const WINDOW: usize = 3;

/// The ids of the practice problems that are open right now.
pub(crate) async fn open_ids(s: &AppState) -> ApiResult<HashSet<String>> {
    let practice: Vec<&Problem> = s.catalog.tracks.iter().filter(|t| t.section == Section::Practice).flat_map(|t| &t.problems).collect();
    if practice.is_empty() {
        return Ok(HashSet::new());
    }
    let attempted: HashSet<String> = store::attempted_dsa(&s.db).await?.into_iter().collect();
    let progress = store::progress(&s.db).await?;
    let settings = crate::settings::srs(&s.db).await?;
    let (coming, _) = next_up_ids(s, &settings, &progress, WINDOW).await?;
    let coming: HashSet<&str> = coming.iter().map(String::as_str).collect();
    Ok(practice
        .into_iter()
        .filter(|p| {
            p.meta.unlocked_by.iter().any(|id| attempted.contains(id)) || (p.meta.warmup && p.meta.unlocked_by.iter().any(|id| coming.contains(id.as_str())))
        })
        .map(|p| p.id.clone())
        .collect())
}

/// Fails with `Locked` when `p` is a practice problem that isn't open yet.
pub(crate) async fn ensure_open(s: &AppState, p: &Problem) -> ApiResult<()> {
    if p.meta.unlocked_by.is_empty() {
        return Ok(());
    }
    if open_ids(s).await?.contains(&p.id) {
        return Ok(());
    }
    let names = unlock_refs(s, p).into_iter().map(|u| u.title).collect::<Vec<_>>().join(" or ");
    Err(ApiError::Locked(format!("{} opens after you log {names} on LeetCode", p.meta.title)))
}

/// The DSA problems that unlock `p`, for display.
pub(crate) fn unlock_refs(s: &AppState, p: &Problem) -> Vec<UnlockRef> {
    p.meta
        .unlocked_by
        .iter()
        .filter_map(|id| s.catalog.problem(id))
        .map(|(_, q)| UnlockRef { id: q.id.clone(), slug: q.meta.slug.clone(), title: q.meta.title.clone() })
        .collect()
}

#[derive(Serialize)]
pub struct PracticeProblem {
    id: String,
    slug: String,
    title: String,
    level: Band,
    order: u32,
    /// The first paragraph of the statement, markdown.
    blurb: String,
    teaches: Vec<String>,
    warmup: bool,
    ready: bool,
    open: bool,
    progress: Progress,
    unlocked_by: Vec<UnlockRef>,
    /// Which of `unlocked_by` has been logged already.
    logged: Vec<String>,
}

#[derive(Serialize)]
pub struct PracticeTrack {
    code: String,
    slug: String,
    name: String,
    summary: String,
    language: Language,
    problems: Vec<PracticeProblem>,
}

/// The practice tracks for a pattern (by its DSA track code, e.g. `D11`), one per language.
pub async fn for_pattern(State(s): State<AppState>, Path(code): Path<String>) -> ApiResult<Json<Vec<PracticeTrack>>> {
    let pattern = s
        .catalog
        .tracks
        .iter()
        .find(|t| t.section == Section::Dsa && (t.code.eq_ignore_ascii_case(&code) || t.slug == code))
        .ok_or_else(|| ApiError::NotFound(format!("pattern {code}")))?;
    let open = open_ids(&s).await?;
    let progress: HashMap<String, ProgressRow> = store::progress(&s.db).await?;
    let attempted: HashSet<String> = store::attempted_dsa(&s.db).await?.into_iter().collect();
    let tracks = s
        .catalog
        .tracks
        .iter()
        .filter(|t| t.section == Section::Practice && t.pattern.as_deref() == Some(pattern.name.as_str()))
        .map(|t| PracticeTrack {
            code: t.code.clone(),
            slug: t.slug.clone(),
            name: t.name.clone(),
            summary: t.summary.clone(),
            language: t.problems.first().map_or(Language::Python, |p| p.meta.language),
            problems: t
                .problems
                .iter()
                .map(|p| PracticeProblem {
                    id: p.id.clone(),
                    slug: p.meta.slug.clone(),
                    title: p.meta.title.clone(),
                    level: p.meta.level,
                    order: p.meta.order,
                    blurb: crate::activity::excerpt(p.files.statement.as_deref().unwrap_or("")),
                    teaches: p.meta.teaches.clone(),
                    warmup: p.meta.warmup,
                    ready: p.meta.status == Status::Ready,
                    open: open.contains(&p.id),
                    progress: Progress::of(progress.get(&p.id)),
                    unlocked_by: unlock_refs(&s, p),
                    logged: p.meta.unlocked_by.iter().filter(|id| attempted.contains(*id)).cloned().collect(),
                })
                .collect(),
        })
        .collect();
    Ok(Json(tracks))
}

/// Practice counts for one pattern's card: how many problems, how many are open, how many solved.
pub(crate) fn counts(s: &AppState, pattern: &str, open: &HashSet<String>, progress: &HashMap<String, ProgressRow>) -> (usize, usize, usize) {
    let problems: Vec<&Problem> = s
        .catalog
        .tracks
        .iter()
        .filter(|t| t.section == Section::Practice && t.pattern.as_deref() == Some(pattern))
        .flat_map(|t| &t.problems)
        .filter(|p| p.meta.status == Status::Ready)
        .collect();
    (problems.len(), problems.iter().filter(|p| open.contains(&p.id)).count(), problems.iter().filter(|p| Progress::of(progress.get(&p.id)).solved()).count())
}
