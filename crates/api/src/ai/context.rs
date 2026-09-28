//! What an answer is grounded in: the problem, your code, your last run, the reference solution (only once you've
//! solved or revealed it), similar problems and your attempts at them, and your stats. Each piece becomes one rig
//! document and one source chip in the UI.

use anneal_content::{Catalog, Problem, Track};
use anneal_runner::{Level, Outcome, RunStatus};
use serde::Serialize;
use sqlx::PgPool;

use super::index::{Index, clip};
use crate::progress;
use crate::store;

/// A piece of context, shown under the answer so you can see what it used.
#[derive(Debug, Clone, Serialize)]
pub struct Source {
    pub kind: &'static str,
    pub label: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub problem_id: Option<String>,
}

#[derive(Default)]
pub struct Grounding {
    pub documents: Vec<(String, String)>,
    pub sources: Vec<Source>,
    /// Whether the reference solution was included (you've solved or revealed it).
    pub reference: bool,
}

impl Grounding {
    fn add(&mut self, id: &str, text: String, source: Source) {
        self.documents.push((id.to_owned(), text));
        self.sources.push(source);
    }
}

pub const SYSTEM: &str = "You are anneal's tutor, helping one engineer prepare for senior Rust backend interviews. \
Answer in Markdown and keep it tight: short paragraphs, ```rust code blocks, no filler. Ground every answer in the \
documents you're given (the problem, their code, their last run, their history and stats) and say so when you use them, \
e.g. \"your last run\" or \"you hit this in D9\". Explain Rust in terms of ownership, borrowing and lifetimes when it \
applies. Unless the request explicitly asks for a full solution, prefer the next step or the smallest change over \
writing the whole answer. If the reference solution is not in the documents, don't pretend to know it.";

/// The prompts behind the quick-action chips.
pub fn action_prompt(action: &str) -> Option<&'static str> {
    Some(match action {
        "explain_error" => "Explain the first error in my last run in plain words: what the compiler is protecting against here, and the smallest fix.",
        "hint" => "Give me one hint for my next step. Don't write the solution.",
        "complexity" => "What are the time and space complexity of my current code? How does that compare with the best approach for this problem's constraints?",
        "similar" => "How did I do on problems similar to this one? What went wrong there that applies here?",
        "review" => "Review my solution like a senior Rust interviewer: correctness risks, idiomatic Rust, performance, and how it compares with the reference.",
        _ => return None,
    })
}

pub struct Ask<'a> {
    pub track: &'a Track,
    pub problem: &'a Problem,
    /// The editor's current code; falls back to the saved draft or the starter.
    pub code: Option<String>,
    /// The question, embedded to find your most relevant past attempts.
    pub query_vector: Option<Vec<f32>>,
}

pub async fn build(db: &PgPool, catalog: &Catalog, index: &Index, ask: Ask<'_>) -> anyhow::Result<Grounding> {
    let (t, p) = (ask.track, ask.problem);
    let mut g = Grounding::default();

    g.add("problem", problem_doc(t, p), Source { kind: "problem", label: format!("{} · {}", t.code, p.meta.title), problem_id: None });

    let code = match ask.code {
        Some(c) => c,
        None => store::draft(db, &p.id).await?.or_else(|| p.files.starter.clone()).unwrap_or_default(),
    };
    g.add("your_code", format!("The code in the editor now (src/lib.rs):\n```rust\n{}\n```", clip(&code, 6000)), Source {
        kind: "code",
        label: "your code".into(),
        problem_id: None,
    });

    if let Some(run) = store::latest_run(db, &p.id).await? {
        let r = &run.result.0;
        let label = match r.status {
            RunStatus::CompileError => {
                let first = r.diagnostics.iter().find(|d| d.level == Level::Error).and_then(|d| d.code.clone());
                format!("last run · {}", first.unwrap_or_else(|| "compile error".into()))
            }
            RunStatus::Timeout => "last run · timed out".into(),
            _ => format!("last run · {}/{} passed", r.passed, r.total),
        };
        g.add("last_run", run_doc(&run), Source { kind: "run", label, problem_id: None });
    }

    let attempt = store::latest_attempt(db, &p.id).await?;
    let revealed = attempt.as_ref().is_some_and(|a| a.solution_revealed);
    if (store::ever_solved(db, &p.id).await? || revealed)
        && let Some(solution) = &p.files.solution
    {
        let notes = p
            .meta
            .solution
            .as_ref()
            .map(|n| format!("\nWhy it works: {}\nTime {} · space {}", n.explanation, n.time, n.space))
            .unwrap_or_default();
        g.add("reference_solution", format!("The reference solution:\n```rust\n{}\n```{notes}", clip(solution, 5000)), Source {
            kind: "reference",
            label: "reference solution".into(),
            problem_id: None,
        });
        g.reference = true;
    }

    // Similar problems, by embedding when available, otherwise by shared tags.
    let similar: Vec<String> = {
        let by_vector = index.similar_problems(&p.id, 3);
        if by_vector.is_empty() { similar_by_tags(catalog, p, 3) } else { by_vector.into_iter().map(|(id, _)| id).collect() }
    };
    let summaries = store::attempt_summaries(db).await?;
    for id in &similar {
        let Some((st, sp)) = catalog.problem(id) else { continue };
        let mine: Vec<&store::AttemptSummary> = summaries.iter().filter(|a| &a.problem_id == id).collect();
        let history = match mine.last() {
            None => "You haven't attempted it.".to_owned(),
            Some(a) => format!(
                "You {} it; errors and lints on the way: {}.",
                if a.solved { if a.assisted { "solved (with help)" } else { "solved" } } else { "attempted but didn't solve" },
                if a.errors.is_empty() { "none".into() } else { a.errors.join(", ") }
            ),
        };
        g.add(
            &format!("similar_{id}"),
            format!("A similar problem, {} · {} ({}): {history}", st.code, sp.meta.title, sp.meta.tags.join(", ")),
            Source { kind: "similar", label: format!("{} {}", st.code, sp.meta.title), problem_id: Some(id.clone()) },
        );
    }

    // Your attempts elsewhere that are closest to the question.
    if let Some(q) = &ask.query_vector {
        for (attempt_id, pid) in index.nearest_attempts(q, 2, &p.id) {
            if similar.contains(&pid) {
                continue;
            }
            let (Some(a), Some((at, ap))) = (summaries.iter().find(|a| a.attempt_id == attempt_id), catalog.problem(&pid)) else {
                continue;
            };
            g.add(
                &format!("your_attempt_{attempt_id}"),
                format!(
                    "Your attempt at {} · {} ({}): errors and lints {}; last code:\n```rust\n{}\n```",
                    at.code,
                    ap.meta.title,
                    if a.solved { "solved" } else { "not solved" },
                    if a.errors.is_empty() { "none".into() } else { a.errors.join(", ") },
                    clip(&a.last_code, 1200)
                ),
                Source { kind: "attempt", label: format!("your {} attempt", at.code), problem_id: Some(pid.clone()) },
            );
        }
    }

    g.add("your_stats", stats_doc(db, catalog).await?, Source { kind: "stats", label: "your stats".into(), problem_id: None });
    Ok(g)
}

fn problem_doc(t: &Track, p: &Problem) -> String {
    let m = &p.meta;
    let mut s = format!(
        "Problem {} · {} in {} ({}), level {:?}, mode {:?}. Tags: {}.\n",
        t.code,
        m.title,
        t.name,
        t.stage(&m.stage).map_or(m.stage.as_str(), |st| st.name.as_str()),
        m.level,
        m.mode,
        m.tags.join(", ")
    );
    if let Some(statement) = &p.files.statement {
        s.push_str(&clip(statement, 5000));
        s.push('\n');
    }
    if !m.constraints.is_empty() {
        s.push_str(&format!("Constraints: {}\n", m.constraints.join("; ")));
    }
    for e in &m.examples {
        s.push_str(&format!("Example: {} → {}\n", e.input, e.output));
    }
    if let Some(r) = &m.rules {
        s.push_str(&format!("Rules for this fix-this problem: {}\n", serde_json::to_string(r).unwrap_or_default()));
    }
    s
}

fn run_doc(run: &store::RunRow) -> String {
    let r = &run.result.0;
    let mut s = format!("Their last {} ({}): {:?}, {}/{} tests passed.\n", run.kind, run.created_at.format("%Y-%m-%d %H:%M UTC"), r.status, r.passed, r.total);
    for d in r.diagnostics.iter().take(4) {
        let rendered = crate::ai::strip_ansi(&d.rendered);
        s.push_str(&format!("{:?} {}: {}\n{}\n", d.level, d.code.as_deref().unwrap_or(""), d.message, clip(&rendered, 1500)));
    }
    for t in r.tests.iter().filter(|t| t.outcome != Outcome::Passed).take(4) {
        s.push_str(&format!("Failing test {} ({:?})", t.name, t.suite));
        if let Some(c) = &t.check {
            s.push_str(&format!(": input {} · expected {} · got {}", c.input, c.expected, c.got));
        } else if let Some(p) = &t.panic {
            s.push_str(&format!(": panicked: {}", clip(p, 400)));
        }
        s.push('\n');
    }
    s
}

async fn stats_doc(db: &PgPool, catalog: &Catalog) -> anyhow::Result<String> {
    let rows = store::activity(db).await?;
    let runs = store::run_stats(db).await?;
    let focus = store::focus(db).await?;
    let st = progress::stats(catalog, &rows, &runs, &focus, chrono::Utc::now());
    let pct = |v: Option<f64>| v.map_or("n/a".to_owned(), |x| format!("{x:.0}%"));
    let list = |v: &[progress::Counted]| {
        v.iter()
            .take(5)
            .map(|c| format!("{} ×{}{}", c.key, c.count, c.where_most.as_deref().map(|w| format!(" (mostly {w})")).unwrap_or_default()))
            .collect::<Vec<_>>()
            .join(", ")
    };
    Ok(format!(
        "Their stats across anneal: first run passes {} of the time; {} runs per solve; {} of runs in the last 30 days \
         didn't compile; {} of unassisted solves within the interview budget. Most frequent errors: {}. Most frequent \
         lints: {}.",
        pct(st.first_run_pass),
        st.runs_per_solve.map_or("n/a".to_owned(), |x| format!("{x:.1}")),
        pct(st.compile_error_rate),
        pct(st.within_budget),
        if st.errors.is_empty() { "none yet".into() } else { list(&st.errors) },
        if st.lints.is_empty() { "none yet".into() } else { list(&st.lints) },
    ))
}

fn similar_by_tags(catalog: &Catalog, p: &Problem, n: usize) -> Vec<String> {
    let mut scored: Vec<(usize, &str)> = catalog
        .tracks
        .iter()
        .flat_map(|t| &t.problems)
        .filter(|q| q.id != p.id && q.files.statement.is_some())
        .map(|q| (q.meta.tags.iter().filter(|t| p.meta.tags.contains(t)).count(), q.id.as_str()))
        .filter(|(n, _)| *n > 0)
        .collect();
    scored.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(b.1)));
    scored.into_iter().take(n).map(|(_, id)| id.to_owned()).collect()
}
