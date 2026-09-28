//! Embeddings for retrieval. Every ready problem and every attempt you've run code in is embedded once (again only
//! when its text changes) and stored in `ai_embeddings`; the vectors are small enough to search in memory.

use std::collections::HashMap;

use anneal_content::{Catalog, Problem, Track};
use sqlx::PgPool;

use crate::store;

/// The in-memory copy of the stored vectors for the configured embedding model.
#[derive(Default)]
pub struct Index {
    problems: Vec<(String, Vec<f32>)>,
    /// `(attempt id, problem id, vector)`.
    attempts: Vec<(i64, String, Vec<f32>)>,
}

impl Index {
    pub fn counts(&self) -> (usize, usize) {
        (self.problems.len(), self.attempts.len())
    }

    /// Problems closest to `id`, best first, excluding itself.
    pub fn similar_problems(&self, id: &str, n: usize) -> Vec<(String, f32)> {
        let Some((_, v)) = self.problems.iter().find(|(p, _)| p == id) else { return Vec::new() };
        top(self.problems.iter().filter(|(p, _)| p != id).map(|(p, w)| (p.clone(), anneal_ai::cosine(v, w))), n)
    }

    /// Your attempts closest to a query vector, as `(attempt id, problem id)`, best first.
    pub fn nearest_attempts(&self, query: &[f32], n: usize, not_problem: &str) -> Vec<(i64, String)> {
        let scored = self
            .attempts
            .iter()
            .filter(|(_, p, _)| p != not_problem)
            .map(|(a, p, v)| ((*a, p.clone()), anneal_ai::cosine(query, v)));
        top(scored, n).into_iter().map(|(k, _)| k).collect()
    }
}

fn top<K>(items: impl Iterator<Item = (K, f32)>, n: usize) -> Vec<(K, f32)> {
    let mut v: Vec<(K, f32)> = items.collect();
    v.sort_by(|a, b| b.1.total_cmp(&a.1));
    v.truncate(n);
    v
}

/// What a problem's vector is made of: enough to recognise what it's about and what it teaches.
pub fn problem_text(t: &Track, p: &Problem) -> String {
    let m = &p.meta;
    let mut s = format!("{} ({} · {:?} · {:?})\nTags: {}\n", m.title, t.name, m.level, m.mode, m.tags.join(", "));
    if !m.teaches.is_empty() {
        s.push_str(&format!("Teaches: {}\n", m.teaches.join(" ")));
    }
    if let Some(statement) = &p.files.statement {
        s.push_str(&clip(statement, 1500));
    }
    s
}

/// An attempt's vector: the problem, what went wrong on the way, and the last code you ran.
pub fn attempt_text(title: &str, tags: &[String], outcome: &str, errors: &[String], code: &str) -> String {
    format!(
        "{title} ({})\nOutcome: {outcome}\nErrors and lints on the way: {}\nFinal code:\n{}",
        tags.join(", "),
        if errors.is_empty() { "none".into() } else { errors.join(", ") },
        clip(code, 1500)
    )
}

pub fn clip(s: &str, max: usize) -> String {
    if s.len() <= max {
        return s.to_owned();
    }
    let mut end = max;
    while !s.is_char_boundary(end) {
        end -= 1;
    }
    format!("{}…", &s[..end])
}

/// FNV-1a: stable across Rust versions (unlike `DefaultHasher`), so unchanged text is never re-embedded.
pub fn hash(s: &str) -> String {
    let mut h: u64 = 0xcbf29ce484222325;
    for b in s.bytes() {
        h ^= u64::from(b);
        h = h.wrapping_mul(0x100000001b3);
    }
    format!("{h:016x}")
}

/// Embeds whatever is new or changed, drops rows for problems that no longer exist, and returns the fresh index.
pub async fn refresh(db: &PgPool, catalog: &Catalog, ai: &anneal_ai::Ai) -> anyhow::Result<Index> {
    let Some(model) = ai.info.embeddings.clone() else { return Ok(Index::default()) };
    let stored: HashMap<(String, String), String> =
        sqlx::query_as::<_, (String, String, String)>("SELECT kind, ref_id, content_hash FROM ai_embeddings WHERE model = $1")
            .bind(&model)
            .fetch_all(db)
            .await?
            .into_iter()
            .map(|(k, r, h)| ((k, r), h))
            .collect();

    let mut wanted: Vec<(&str, String, String)> = Vec::new(); // (kind, ref, text)
    for t in &catalog.tracks {
        for p in t.problems.iter().filter(|p| p.files.statement.is_some()) {
            wanted.push(("problem", p.id.clone(), problem_text(t, p)));
        }
    }
    for a in store::attempt_summaries(db).await? {
        let Some((_, p)) = catalog.problem(&a.problem_id) else { continue };
        let outcome = match (a.solved, a.assisted) {
            (true, false) => "solved unassisted",
            (true, true) => "solved with help",
            (false, _) => "not solved yet",
        };
        wanted.push(("attempt", a.attempt_id.to_string(), attempt_text(&p.meta.title, &p.meta.tags, outcome, &a.errors, &a.last_code)));
    }

    let todo: Vec<&(&str, String, String)> =
        wanted.iter().filter(|(k, r, text)| stored.get(&(k.to_string(), r.clone())) != Some(&hash(text))).collect();
    if !todo.is_empty() {
        tracing::info!(count = todo.len(), %model, "embedding new or changed items");
        let vectors = ai.embed(todo.iter().map(|(_, _, text)| text.clone()).collect()).await?;
        let mut tx = db.begin().await?;
        for ((kind, r, text), v) in todo.iter().zip(vectors) {
            sqlx::query(
                "INSERT INTO ai_embeddings (kind, ref_id, model, content_hash, embedding) VALUES ($1, $2, $3, $4, $5)
                 ON CONFLICT (kind, ref_id, model) DO UPDATE
                 SET content_hash = EXCLUDED.content_hash, embedding = EXCLUDED.embedding, updated_at = now()",
            )
            .bind(kind)
            .bind(r)
            .bind(&model)
            .bind(hash(text))
            .bind(&v)
            .execute(&mut *tx)
            .await?;
        }
        tx.commit().await?;
    }
    // Problems that were removed or renamed.
    let current: Vec<String> = wanted.iter().filter(|(k, _, _)| *k == "problem").map(|(_, r, _)| r.clone()).collect();
    sqlx::query("DELETE FROM ai_embeddings WHERE kind = 'problem' AND NOT (ref_id = ANY($1))").bind(&current).execute(db).await?;

    load(db, &model).await
}

async fn load(db: &PgPool, model: &str) -> anyhow::Result<Index> {
    let rows: Vec<(String, String, Vec<f32>)> =
        sqlx::query_as("SELECT kind, ref_id, embedding FROM ai_embeddings WHERE model = $1").bind(model).fetch_all(db).await?;
    let problem_of: HashMap<i64, String> = sqlx::query_as::<_, (i64, String)>("SELECT id, problem_id FROM attempts")
        .fetch_all(db)
        .await?
        .into_iter()
        .collect();
    let mut index = Index::default();
    for (kind, r, v) in rows {
        match kind.as_str() {
            "problem" => index.problems.push((r, v)),
            _ => {
                if let Ok(id) = r.parse::<i64>()
                    && let Some(p) = problem_of.get(&id)
                {
                    index.attempts.push((id, p.clone(), v));
                }
            }
        }
    }
    Ok(index)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hash_is_stable_and_clip_respects_char_boundaries() {
        assert_eq!(hash("anneal"), hash("anneal"));
        assert_ne!(hash("anneal"), hash("anneal "));
        assert_eq!(clip("héllo", 2), "h…");
        assert_eq!(clip("short", 10), "short");
    }
}
