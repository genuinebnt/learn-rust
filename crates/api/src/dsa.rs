//! The DSA section: the NeetCode lists you solve on LeetCode and log here. See docs/DSA.md.
//!
//! `GET /api/dsa` is everything the home and plan screens need. `POST /api/dsa/problems/{id}/log` records how a
//! problem went (it feeds streaks, readiness and the review schedule like any solve), and `POST /api/dsa/start`
//! moves where "next problem" starts from.

use std::collections::HashMap;

use anneal_content::{Band, Catalog, Company, CompanyGroup, DsaProblem, Problem, Role, Section, Technique, Track};
use axum::Json;
use axum::extract::{Path, State};
use chrono::NaiveDate;
use serde::{Deserialize, Serialize};

use crate::AppState;
use crate::dsa_next::{self, Entry};
use crate::error::{ApiError, ApiResult};
use crate::reviews::{self, Grade, Pace, Settings};
use crate::store::{self, ProgressRow, ReviewRow};

#[derive(Serialize)]
pub struct Overview<'a> {
    today: NaiveDate,
    settings: Settings,
    patterns: Vec<PatternRow<'a>>,
    techniques: &'a [Technique],
    company_groups: &'a [CompanyGroup],
    problems: Vec<ProblemRow<'a>>,
    plan: Plan,
}

#[derive(Serialize)]
struct PatternRow<'a> {
    code: &'a str,
    slug: &'a str,
    name: &'a str,
    total: usize,
    in_150: usize,
    solved: usize,
}

#[derive(Serialize)]
struct ProblemRow<'a> {
    id: &'a str,
    slug: &'a str,
    number: u32,
    title: &'a str,
    difficulty: Band,
    /// The track code, e.g. `D7`.
    pattern: &'a str,
    lists: &'a [String],
    premium: bool,
    tags: &'a [String],
    companies: &'a [Company],
    video: Option<&'a str>,
    technique: &'a str,
    role: Role,
    practice_of: Option<&'a str>,
    order: u32,
    /// A written lesson exists for it.
    has_page: bool,
    state: Standing,
}

/// How a problem stands: nothing yet, or the latest review's grade.
#[derive(Serialize)]
struct Standing {
    /// Solved at least once.
    solved: bool,
    /// The latest attempt needed help.
    assisted: bool,
    last_grade: Option<String>,
    reps: i32,
    lapses: i32,
    last_review: Option<NaiveDate>,
    due: Option<NaiveDate>,
    retrievability: Option<f32>,
}

#[derive(Serialize)]
struct Plan {
    /// Problems the goal counts, and how many are done.
    goal_total: u32,
    goal_done: u32,
    pace: Pace,
    /// The next problems in order, from `start`.
    next_up: Vec<String>,
    start: Option<String>,
    /// Today is a day for a new problem (`new_days`).
    solve_day: bool,
    /// Reviews today can take.
    capacity: u32,
    /// Today's reviews: most forgotten first, up to the capacity.
    review_ids: Vec<String>,
    /// Reviews due now, and how many of those are past their day.
    due: usize,
    overdue: usize,
}

fn local(t: chrono::DateTime<chrono::Utc>) -> NaiveDate {
    t.with_timezone(&chrono::Local).date_naive()
}

fn dsa_tracks(catalog: &Catalog) -> impl Iterator<Item = &Track> {
    catalog.tracks.iter().filter(|t| t.section == Section::Dsa)
}

fn dsa_of(p: &Problem) -> &DsaProblem {
    p.dsa.as_ref().expect("DSA tracks only hold DSA problems")
}

fn state_of(progress: Option<&ProgressRow>, review: Option<&ReviewRow>, today: NaiveDate) -> Standing {
    Standing {
        solved: progress.is_some_and(|p| p.solved),
        assisted: progress.is_some_and(|p| p.assisted),
        last_grade: review.map(|r| r.last_grade.clone()),
        reps: review.map_or(0, |r| r.reps),
        lapses: review.map_or(0, |r| r.lapses),
        last_review: review.map(|r| local(r.last_review)),
        due: review.map(|r| local(r.due_at)),
        retrievability: review.map(|r| r.retrievability(today)),
    }
}

fn row<'a>(t: &'a Track, p: &'a Problem, progress: &HashMap<String, ProgressRow>, reviews: &HashMap<&str, &ReviewRow>, today: NaiveDate) -> ProblemRow<'a> {
    let d = dsa_of(p);
    ProblemRow {
        id: &p.id,
        slug: &d.slug,
        number: d.number,
        title: &p.meta.title,
        difficulty: p.meta.level,
        pattern: &t.code,
        lists: &d.lists,
        premium: d.premium,
        tags: &p.meta.tags,
        companies: &d.companies,
        video: d.video.as_deref(),
        technique: &d.technique,
        role: d.role,
        practice_of: d.practice_of.as_deref(),
        order: p.meta.order,
        has_page: d.page.is_some(),
        state: state_of(progress.get(&p.id), reviews.get(p.id.as_str()).copied(), today),
    }
}

/// Whether a problem counts toward the goal's list.
fn in_goal(p: &Problem, settings: &Settings) -> bool {
    let d = dsa_of(p);
    d.lists.contains(&settings.goal.list) && !(settings.goal.free_only && d.premium)
}

async fn plan(s: &AppState, settings: &Settings, progress: &HashMap<String, ProgressRow>, reviews: &[ReviewRow], today: NaiveDate) -> ApiResult<Plan> {
    let solved = |p: &Problem| progress.get(&p.id).is_some_and(|r| r.solved);
    let all: Vec<&Problem> = dsa_tracks(&s.catalog).flat_map(|t| &t.problems).collect();

    let goal: Vec<&Problem> = all.iter().copied().filter(|p| in_goal(p, settings)).collect();
    let goal_done = goal.iter().filter(|p| solved(p)).count() as u32;
    // Problems beyond the list (a few from the 250) count against `extra`.
    let beyond = all.iter().filter(|p| !in_goal(p, settings) && dsa_of(p).lists.iter().any(|l| l == "neetcode250") && solved(p)).count() as u32;
    let extra_done = beyond.min(settings.goal.extra);
    let goal_total = goal.len() as u32 + settings.goal.extra;
    let remaining = settings.goal.custom_left.unwrap_or_else(|| goal_total.saturating_sub(goal_done + extra_done));

    // "Next problem" walks the goal's list; once it's done, the 250, then everything.
    let scope = |list: &str| -> Vec<&Problem> { all.iter().copied().filter(|p| dsa_of(p).lists.iter().any(|l| l == list)).collect() };
    let start = store::dsa_start(&s.db).await?;
    let mut next_up = Vec::new();
    for pool in [goal.clone(), scope("neetcode250"), scope("all")] {
        let entries: Vec<Entry> = pool.iter().map(|p| Entry { id: &p.id, done: solved(p) }).collect();
        next_up = dsa_next::next_up(&entries, start.as_deref(), 5).into_iter().map(str::to_owned).collect();
        if !next_up.is_empty() {
            break;
        }
    }

    let cards: Vec<(String, fsrs::MemoryState, NaiveDate, NaiveDate)> =
        reviews.iter().map(|r| (r.problem_id.clone(), r.memory(), local(r.last_review), local(r.due_at))).collect();
    let due = cards.iter().filter(|c| c.3 <= today).count();
    let overdue = cards.iter().filter(|c| c.3 < today).count();
    Ok(Plan {
        goal_total,
        goal_done: goal_done + extra_done,
        pace: reviews::pace(remaining, today, settings),
        next_up,
        start,
        solve_day: settings.is_solve_day(today),
        capacity: settings.capacity_on(today),
        review_ids: reviews::pick(today, settings, &cards),
        due,
        overdue,
    })
}

/// The reviews that belong to DSA problems.
fn dsa_reviews(catalog: &Catalog, rows: Vec<ReviewRow>) -> Vec<ReviewRow> {
    rows.into_iter().filter(|r| catalog.problem(&r.problem_id).is_some_and(|(_, p)| p.dsa.is_some())).collect()
}

pub async fn overview(State(s): State<AppState>) -> ApiResult<Json<serde_json::Value>> {
    let today = crate::activity::today();
    let settings = crate::settings::srs(&s.db).await?;
    let progress = store::progress(&s.db).await?;
    let reviews = dsa_reviews(&s.catalog, store::reviews(&s.db).await?);
    let by_problem: HashMap<&str, &ReviewRow> = reviews.iter().map(|r| (r.problem_id.as_str(), r)).collect();

    let patterns = dsa_tracks(&s.catalog)
        .map(|t| PatternRow {
            code: &t.code,
            slug: &t.slug,
            name: &t.name,
            total: t.problems.len(),
            in_150: t.problems.iter().filter(|p| dsa_of(p).lists.iter().any(|l| l == "neetcode150")).count(),
            solved: t.problems.iter().filter(|p| progress.get(&p.id).is_some_and(|r| r.solved)).count(),
        })
        .collect();
    let problems = dsa_tracks(&s.catalog).flat_map(|t| t.problems.iter().map(move |p| (t, p))).map(|(t, p)| row(t, p, &progress, &by_problem, today)).collect();
    let plan = plan(&s, &settings, &progress, &reviews, today).await?;
    let overview = Overview {
        today,
        settings,
        patterns,
        techniques: &s.catalog.dsa.techniques,
        company_groups: &s.catalog.dsa.company_groups,
        problems,
        plan,
    };
    // Plain data, so serializing can't fail; the value only exists to end the borrow of the catalog.
    Ok(Json(serde_json::to_value(&overview).expect("overview is plain data")))
}

/// The written lesson for a problem, if one has been written.
pub async fn page(State(s): State<AppState>, Path(id): Path<String>) -> ApiResult<Json<Option<anneal_content::Page>>> {
    let (_, p) = s.catalog.problem(&id).ok_or_else(|| ApiError::NotFound(format!("problem {id}")))?;
    let dsa = p.dsa.as_ref().ok_or_else(|| ApiError::BadRequest(format!("{id} isn't a DSA problem")))?;
    Ok(Json(dsa.page.clone()))
}

#[derive(Deserialize)]
pub struct LogBody {
    grade: Grade,
}

#[derive(Serialize)]
pub struct Logged {
    id: String,
    /// When it comes back for review.
    due: NaiveDate,
    /// Days until then, before it was moved to a day with room.
    ideal_days: f32,
}

/// Records how a problem went: `again` (couldn't yet), `hard` (with help), `good` (on my own) or `easy`.
pub async fn log(State(s): State<AppState>, Path(id): Path<String>, Json(body): Json<LogBody>) -> ApiResult<Json<Logged>> {
    let (_, p) = s.catalog.problem(&id).ok_or_else(|| ApiError::NotFound(format!("problem {id}")))?;
    if p.dsa.is_none() {
        return Err(ApiError::BadRequest(format!("{id} isn't a DSA problem; solve it in the workspace")));
    }
    let settings = crate::settings::srs(&s.db).await?;
    let scheduled = store::log_attempt(&s.db, &id, body.grade, &settings).await?;
    // The next problem follows from the one just done.
    store::set_dsa_start(&s.db, &id).await?;
    Ok(Json(Logged { id, due: scheduled.due, ideal_days: scheduled.ideal_days }))
}

#[derive(Deserialize)]
pub struct StartBody {
    /// A problem id, or a track slug or code to start at its first problem.
    from: String,
}

/// Moves where "next problem" starts from.
pub async fn start(State(s): State<AppState>, Json(body): Json<StartBody>) -> ApiResult<Json<serde_json::Value>> {
    let id = match s.catalog.problem(&body.from) {
        Some((_, p)) if p.dsa.is_some() => p.id.clone(),
        Some(_) => return Err(ApiError::BadRequest(format!("{} isn't a DSA problem", body.from))),
        None => dsa_tracks(&s.catalog)
            .find(|t| t.slug == body.from || t.code.eq_ignore_ascii_case(&body.from))
            .and_then(|t| t.problems.first())
            .map(|p| p.id.clone())
            .ok_or_else(|| ApiError::NotFound(format!("problem or track {}", body.from)))?,
    };
    store::set_dsa_start(&s.db, &id).await?;
    Ok(Json(serde_json::json!({ "start": id })))
}
