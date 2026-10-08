//! LeetCode's problem statement and hints for a DSA problem (docs/DSA.md, decision 5).
//!
//! `GET /api/dsa/problems/{id}/statement` fetches the statement from LeetCode the first time, cleans its HTML, and keeps
//! it in `dsa_statements` for a month, so the page works offline afterwards and LeetCode is asked once per problem. A
//! Premium problem has no public statement; it is reported as `locked`. If LeetCode can't be reached, an older copy is
//! served when there is one.

use std::time::Duration;

use axum::Json;
use axum::extract::{Path, State};
use chrono::{DateTime, TimeDelta, Utc};
use serde::Serialize;
use serde_json::{Value, json};
use sqlx::types::Json as Jsonb;

use crate::AppState;
use crate::error::{ApiError, ApiResult};

const QUERY: &str = "query($s:String!){question(titleSlug:$s){content hints isPaidOnly}}";
const FRESH_DAYS: i64 = 30;

/// A stored statement: html, hints, locked, when it was fetched.
type Stored = (Option<String>, Jsonb<Vec<String>>, bool, DateTime<Utc>);

#[derive(Serialize)]
pub struct Statement {
    /// Sanitised HTML, or none for a Premium problem.
    html: Option<String>,
    hints: Vec<String>,
    locked: bool,
    fetched_at: DateTime<Utc>,
    /// An older copy, served because LeetCode couldn't be reached.
    stale: bool,
}

/// LeetCode's HTML with everything that could run script or load something unexpected removed. Only what a statement
/// needs stays: text, code, lists, tables, images and links (which open in a new tab).
pub fn sanitize(html: &str) -> String {
    // LeetCode pads its HTML with empty paragraphs (a lone non-breaking space), which only make gaps.
    let html = html.replace("<p>&nbsp;</p>", "").replace("<p> </p>", "");
    ammonia::Builder::default()
        .add_tags(["sup", "sub", "pre", "code", "table", "thead", "tbody", "tr", "th", "td"])
        .link_rel(Some("noopener noreferrer"))
        .set_tag_attribute_value("a", "target", "_blank")
        .clean(&html)
        .to_string()
}

async fn fetch(slug: &str) -> Result<(Option<String>, Vec<String>, bool), String> {
    let base = std::env::var("ANNEAL_LEETCODE_URL").unwrap_or_else(|_| "https://leetcode.com/graphql".into());
    let client = reqwest::Client::builder().timeout(Duration::from_secs(12)).build().map_err(|e| e.to_string())?;
    let response = client
        .post(base)
        .header("Referer", "https://leetcode.com")
        .header("User-Agent", "anneal-dsa")
        .json(&json!({ "query": QUERY, "variables": { "s": slug } }))
        .send()
        .await
        .map_err(|e| e.to_string())?
        .error_for_status()
        .map_err(|e| e.to_string())?;
    let body: Value = response.json().await.map_err(|e| e.to_string())?;
    let question = body.pointer("/data/question").filter(|q| !q.is_null()).ok_or_else(|| format!("LeetCode has no problem called {slug}"))?;
    let locked = question["isPaidOnly"].as_bool().unwrap_or(false);
    let html = question["content"].as_str().map(sanitize).filter(|h| !h.trim().is_empty());
    let hints = question["hints"].as_array().map(|a| a.iter().filter_map(Value::as_str).map(sanitize).collect()).unwrap_or_default();
    Ok((html, hints, locked || question["content"].is_null()))
}

pub async fn get(State(s): State<AppState>, Path(id): Path<String>) -> ApiResult<Json<Statement>> {
    let (_, p) = s.catalog.problem(&id).ok_or_else(|| ApiError::NotFound(format!("problem {id}")))?;
    let dsa = p.dsa.as_ref().ok_or_else(|| ApiError::BadRequest(format!("{id} isn't a DSA problem")))?;
    let slug = dsa.slug.as_str();

    let cached: Option<Stored> =
        sqlx::query_as("SELECT html, hints, locked, fetched_at FROM dsa_statements WHERE slug = $1").bind(slug).fetch_optional(&s.db).await?;
    let as_statement = |(html, hints, locked, fetched_at): Stored, stale: bool| Statement { html, hints: hints.0, locked, fetched_at, stale };
    if let Some(row) = &cached
        && Utc::now() - row.3 < TimeDelta::days(FRESH_DAYS)
    {
        return Ok(Json(as_statement(row.clone(), false)));
    }
    match fetch(slug).await {
        Ok((html, hints, locked)) => {
            let now = Utc::now();
            sqlx::query(
                "INSERT INTO dsa_statements (slug, html, hints, locked, fetched_at) VALUES ($1, $2, $3, $4, $5)
                 ON CONFLICT (slug) DO UPDATE SET html = EXCLUDED.html, hints = EXCLUDED.hints, locked = EXCLUDED.locked, fetched_at = EXCLUDED.fetched_at",
            )
            .bind(slug)
            .bind(&html)
            .bind(Jsonb(&hints))
            .bind(locked)
            .bind(now)
            .execute(&s.db)
            .await?;
            Ok(Json(Statement { html, hints, locked, fetched_at: now, stale: false }))
        }
        Err(message) => match cached {
            Some(row) => Ok(Json(as_statement(row, true))),
            None => Err(ApiError::Upstream(format!("couldn't fetch the statement from LeetCode: {message}"))),
        },
    }
}

#[cfg(test)]
mod tests {
    use super::sanitize;

    #[test]
    fn a_statement_keeps_its_text_and_loses_anything_that_runs() {
        let dirty = r#"<p>Given <code>nums</code>, return <strong>true</strong>.</p><script>alert(1)</script><img src="https://assets.leetcode.com/a.png" onerror="alert(2)"><a href="javascript:alert(3)">x</a><a href="https://leetcode.com/problems/two-sum/">two sum</a><pre>1 &lt;= n</pre><sup>2</sup><p>&nbsp;</p><p>End.</p>"#;
        let clean = sanitize(dirty);
        assert!(!clean.contains("&nbsp;") && clean.contains("<p>End.</p>"), "{clean}");
        assert!(clean.contains("<code>nums</code>") && clean.contains("<strong>true</strong>") && clean.contains("<pre>1 &lt;= n</pre>") && clean.contains("<sup>2</sup>"), "{clean}");
        assert!(!clean.contains("script") && !clean.contains("alert") && !clean.contains("onerror") && !clean.contains("javascript:"), "{clean}");
        assert!(clean.contains(r#"href="https://leetcode.com/problems/two-sum/""#) && clean.contains(r#"target="_blank""#) && clean.contains("noopener"), "{clean}");
        assert!(clean.contains(r#"src="https://assets.leetcode.com/a.png""#), "{clean}");
    }
}
