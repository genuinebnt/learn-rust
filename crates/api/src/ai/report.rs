//! The "Your patterns" report on the Progress page. The numbers are computed here from your runs and attempts; the
//! model only turns them into observations and picks what to practise next from a candidate list, as JSON.

use std::collections::HashMap;

use anneal_content::{Catalog, Status as ContentStatus};
use axum::Json;
use axum::extract::State;
use serde::{Deserialize, Serialize};

use crate::error::{ApiError, ApiResult};
use crate::{AppState, progress, store};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Report {
    pub summary: String,
    pub patterns: Vec<Pattern>,
    /// Where the failing runs went, computed exactly (not by the model).
    pub time_split: Vec<Share>,
    pub next: Vec<Next>,
    pub based_on: Basis,
    #[serde(default)]
    pub generated_at: Option<chrono::DateTime<chrono::Utc>>,
    #[serde(default)]
    pub model: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Pattern {
    /// `error`, `lint`, `strength`, `time` or `habit`.
    pub kind: String,
    /// A short tag like `E0502`, `clippy`, `strength`.
    pub label: String,
    pub title: String,
    pub detail: String,
    /// The numbers behind it, e.g. "23 runs · 9 problems".
    pub evidence: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Share {
    pub label: String,
    pub percent: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Next {
    pub problem_id: String,
    pub title: String,
    pub track: String,
    pub reason: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Basis {
    pub attempts: usize,
    pub runs: usize,
}

/// Errors the borrow checker raises: moves, borrows, lifetimes.
const BORROW_CODES: &[&str] = &["E0382", "E0499", "E0502", "E0503", "E0505", "E0506", "E0507", "E0515", "E0596", "E0597", "E0716", "E0373", "E0106", "E0621", "E0495"];

pub async fn get_patterns(State(s): State<AppState>) -> ApiResult<Json<Option<Report>>> {
    Ok(Json(store::ai_report(&s.db, "patterns").await?.and_then(|(content, model, at)| {
        let mut r: Report = serde_json::from_value(content).ok()?;
        r.generated_at = Some(at);
        r.model = Some(model);
        Some(r)
    })))
}

pub async fn refresh_patterns(State(s): State<AppState>) -> ApiResult<Json<Report>> {
    let ai = s.ai.get().await.ok_or(ApiError::AiOff)?;
    let rows = store::activity(&s.db).await?;
    let runs = store::run_stats(&s.db).await?;
    let focus = store::focus(&s.db).await?;
    if runs.is_empty() {
        return Err(ApiError::BadRequest("solve a few problems first: there are no runs to learn from yet".into()));
    }
    let stats = progress::stats(&s.catalog, &rows, &runs, &focus, chrono::Utc::now());
    let time_split = time_split(&runs);
    let candidates = candidates(&s.catalog, &rows, &stats);

    let facts = serde_json::json!({
        "attempts": rows.len(),
        "runs": runs.len(),
        "solved": rows.iter().filter(|r| r.solved_at.is_some()).count(),
        "assisted_solves": rows.iter().filter(|r| r.solved_at.is_some() && r.assisted).count(),
        "stats": stats,
        "time_split": time_split,
        "per_track": per_track(&s.catalog, &rows),
    });
    let candidate_list: Vec<serde_json::Value> = candidates
        .iter()
        .map(|(id, why)| {
            let (t, p) = s.catalog.problem(id).expect("candidates come from the catalog");
            serde_json::json!({ "problem_id": id, "title": p.meta.title, "track": t.code, "tags": p.meta.tags, "why_candidate": why })
        })
        .collect();

    let prompt = format!(
        "From these facts about my Rust interview practice, write my patterns report, speaking to me as \"you\".\n\
         Facts: {facts}\nCandidate problems to practise next: {candidates}\n\n\
         Reply with only a JSON object, no Markdown fence: {{\"summary\": string (two sentences), \"patterns\": [4 to 6 \
         objects {{\"kind\": \"error\"|\"lint\"|\"strength\"|\"time\"|\"habit\", \"label\": short tag like \"E0502\", \
         \"title\": one line, \"detail\": two sentences grounded in the facts, \"evidence\": the numbers behind it}}], \
         \"next\": [3 objects {{\"problem_id\": one of the candidates' problem_id, \"reason\": short}}]}}. Use only numbers \
         from the facts. Include at least one strength if the facts support one.",
        candidates = serde_json::Value::Array(candidate_list),
    );
    let text = ai
        .ai
        .complete(anneal_ai::Request {
            system: "You analyse coding-practice data and reply with strict JSON only. Address the engineer as \"you\".".into(),
            history: Vec::new(),
            prompt,
            context: Vec::new(),
            max_tokens: 3000,
        })
        .await
        .map_err(|e| ApiError::Ai(ai.ai.redact(&format!("{e:#}"))))?;

    let generated: Generated = parse_json(&text).map_err(|e| ApiError::Ai(format!("the model's report wasn't valid JSON: {e}")))?;
    let next = generated
        .next
        .into_iter()
        .filter_map(|n| {
            let (t, p) = s.catalog.problem(&n.problem_id)?;
            Some(Next { title: p.meta.title.clone(), track: t.code.clone(), problem_id: n.problem_id, reason: n.reason })
        })
        .take(3)
        .collect();
    let report = Report {
        summary: generated.summary,
        patterns: generated.patterns.into_iter().take(6).collect(),
        time_split,
        next,
        based_on: Basis { attempts: rows.len(), runs: runs.len() },
        generated_at: None,
        model: None,
    };
    store::save_ai_report(&s.db, "patterns", &serde_json::to_value(&report).unwrap_or_default(), &ai.ai.info.model).await?;
    get_patterns(State(s)).await.map(|Json(r)| Json(r.expect("just saved")))
}

#[derive(Deserialize)]
struct Generated {
    summary: String,
    patterns: Vec<Pattern>,
    #[serde(default)]
    next: Vec<GeneratedNext>,
}

#[derive(Deserialize)]
struct GeneratedNext {
    problem_id: String,
    reason: String,
}

/// Models sometimes wrap JSON in a Markdown fence despite being asked not to.
fn parse_json<T: serde::de::DeserializeOwned>(text: &str) -> serde_json::Result<T> {
    let t = text.trim();
    let t = t.strip_prefix("```json").or_else(|| t.strip_prefix("```")).unwrap_or(t);
    let t = t.strip_suffix("```").unwrap_or(t).trim();
    let start = t.find('{').unwrap_or(0);
    let end = t.rfind('}').map_or(t.len(), |i| i + 1);
    serde_json::from_str(&t[start..end])
}

/// Where failing runs went: borrow checker, other compile errors, wrong answers, timeouts.
fn time_split(runs: &[store::RunStat]) -> Vec<Share> {
    let failing: Vec<&store::RunStat> = runs.iter().filter(|r| r.status != "passed").collect();
    if failing.is_empty() {
        return Vec::new();
    }
    let mut counts: HashMap<&str, usize> = HashMap::new();
    for r in &failing {
        let key = match r.status.as_str() {
            "compile_error" => {
                let borrow = r.diagnostics.0.iter().any(|d| d.code.as_deref().is_some_and(|c| BORROW_CODES.contains(&c)));
                if borrow { "Borrow checker errors" } else { "Other compile errors" }
            }
            "timeout" => "Timeouts",
            _ => "Failing tests",
        };
        *counts.entry(key).or_default() += 1;
    }
    let mut v: Vec<Share> = counts
        .into_iter()
        .map(|(label, n)| Share { label: label.to_owned(), percent: (n * 100 / failing.len()) as u32 })
        .collect();
    v.sort_by(|a, b| b.percent.cmp(&a.percent).then(a.label.cmp(&b.label)));
    v
}

fn per_track(catalog: &Catalog, rows: &[store::ActivityRow]) -> serde_json::Value {
    let mut m: HashMap<String, (usize, usize, usize)> = HashMap::new(); // attempts, solved, assisted
    for r in rows {
        let Some((t, _)) = catalog.problem(&r.problem_id) else { continue };
        let e = m.entry(format!("{} {}", t.code, t.name)).or_default();
        e.0 += 1;
        if r.solved_at.is_some() {
            e.1 += 1;
            if r.assisted {
                e.2 += 1;
            }
        }
    }
    serde_json::to_value(m.into_iter().map(|(k, (a, s, h))| (k, serde_json::json!({ "attempts": a, "solved": s, "assisted": h }))).collect::<HashMap<_, _>>())
        .unwrap_or_default()
}

/// Unsolved, ready problems in the places your errors cluster, plus the next unsolved ones in tracks you've started.
fn candidates(catalog: &Catalog, rows: &[store::ActivityRow], stats: &progress::Stats) -> Vec<(String, String)> {
    let solved: Vec<&str> = rows.iter().filter(|r| r.solved_at.is_some()).map(|r| r.problem_id.as_str()).collect();
    let open = |p: &anneal_content::Problem| p.meta.status == ContentStatus::Ready && !solved.contains(&p.id.as_str());
    let mut out: Vec<(String, String)> = Vec::new();
    for c in stats.errors.iter().chain(&stats.lints).take(6) {
        let Some(place) = &c.where_most else { continue };
        let code = place.split(" · ").next().unwrap_or_default();
        if let Some(t) = catalog.tracks.iter().find(|t| t.code == code) {
            for p in t.problems.iter().filter(|p| open(p)).take(3) {
                out.push((p.id.clone(), format!("{} clusters in {place}", c.key)));
            }
        }
    }
    let started: Vec<&str> = rows.iter().filter_map(|r| catalog.problem(&r.problem_id)).map(|(t, _)| t.code.as_str()).collect();
    for t in catalog.tracks.iter().filter(|t| started.contains(&t.code.as_str())) {
        if let Some(p) = t.problems.iter().find(|p| open(p)) {
            out.push((p.id.clone(), format!("next unsolved in {}", t.code)));
        }
    }
    out.dedup_by(|a, b| a.0 == b.0);
    out.truncate(15);
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn json_is_found_inside_a_fence_or_prose() {
        #[derive(Deserialize)]
        struct X {
            a: u8,
        }
        assert_eq!(parse_json::<X>("```json\n{\"a\": 1}\n```").unwrap().a, 1);
        assert_eq!(parse_json::<X>("Here you go: {\"a\": 2} hope it helps").unwrap().a, 2);
        assert!(parse_json::<X>("no json").is_err());
    }
}
