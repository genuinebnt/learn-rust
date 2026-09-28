//! The AI assistant: a chat per problem grounded in your code, runs and history (retrieval over embeddings), similar
//! problems, and a report of your patterns. It's off unless a provider key is set on the server
//! ([`anneal_ai::Ai::from_env`]); everything else works the same without it. See docs/AI.md.

mod context;
mod index;
mod report;
mod settings;

use std::convert::Infallible;
use std::sync::Arc;

use axum::Json;
use axum::extract::{Path, State};
use axum::response::sse::{Event, KeepAlive, Sse};
use futures_util::{Stream, StreamExt};
use serde::{Deserialize, Serialize};
use tokio::sync::{RwLock, mpsc};

use crate::error::{ApiError, ApiResult};
use crate::{AppState, store};
pub use index::Index;

/// The configured model and the in-memory embedding index.
pub struct AiState {
    pub ai: anneal_ai::Ai,
    pub index: RwLock<Index>,
}

impl AiState {
    pub fn new(ai: anneal_ai::Ai) -> Arc<Self> {
        Arc::new(AiState { ai, index: RwLock::new(Index::default()) })
    }
}

/// The current assistant, if any. Saving or removing a key in the settings swaps it without a restart.
#[derive(Default)]
pub struct AiSlot(RwLock<Option<Arc<AiState>>>);

impl AiSlot {
    pub fn new(ai: Option<Arc<AiState>>) -> Arc<Self> {
        Arc::new(AiSlot(RwLock::new(ai)))
    }

    pub async fn get(&self) -> Option<Arc<AiState>> {
        self.0.read().await.clone()
    }

    async fn set(&self, ai: Option<Arc<AiState>>) {
        *self.0.write().await = ai;
    }
}

/// Where the assistant's configuration comes from: a key saved in the settings wins over the environment.
pub async fn configure(db: &sqlx::PgPool) -> anyhow::Result<Option<anneal_ai::Ai>> {
    if let Some(saved) = settings::load(db).await? {
        return Ok(Some(anneal_ai::Ai::new(saved.config())?));
    }
    anneal_ai::Ai::from_env()
}

/// Embeds new or changed problems and attempts, then swaps in the fresh index. Runs at startup and after a solve.
pub fn refresh_in_background(s: &AppState) {
    let slot = s.ai.clone();
    let (db, catalog) = (s.db.clone(), s.catalog.clone());
    tokio::spawn(async move {
        let Some(ai) = slot.get().await else { return };
        match index::refresh(&db, &catalog, &ai.ai).await {
            Ok(fresh) => *ai.index.write().await = fresh,
            Err(e) => tracing::warn!(error = %e, "AI index refresh failed"),
        }
    });
}

pub(crate) fn strip_ansi(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut chars = s.chars().peekable();
    while let Some(c) = chars.next() {
        if c == '\u{1b}' && chars.peek() == Some(&'[') {
            for c in chars.by_ref() {
                if c.is_ascii_alphabetic() {
                    break;
                }
            }
        } else {
            out.push(c);
        }
    }
    out
}

async fn ai(s: &AppState) -> ApiResult<Arc<AiState>> {
    s.ai.get().await.ok_or(ApiError::AiOff)
}

// ---------------------------------------------------------------- status

#[derive(Serialize)]
pub struct Status {
    pub enabled: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub info: Option<anneal_ai::Info>,
    pub indexed_problems: usize,
    pub indexed_attempts: usize,
}

pub async fn status(State(s): State<AppState>) -> Json<Status> {
    match &s.ai.get().await {
        None => Json(Status { enabled: false, info: None, indexed_problems: 0, indexed_attempts: 0 }),
        Some(ai) => {
            let (problems, attempts) = ai.index.read().await.counts();
            Json(Status { enabled: true, info: Some(ai.ai.info.clone()), indexed_problems: problems, indexed_attempts: attempts })
        }
    }
}

// ---------------------------------------------------------------- chat

pub async fn history(State(s): State<AppState>, Path(id): Path<String>) -> ApiResult<Json<Vec<store::AiMessage>>> {
    crate::routes::find(&s, &id)?;
    Ok(Json(store::ai_messages(&s.db, &id).await?))
}

pub async fn clear(State(s): State<AppState>, Path(id): Path<String>) -> ApiResult<Json<()>> {
    crate::routes::find(&s, &id)?;
    store::clear_ai_messages(&s.db, &id).await?;
    Ok(Json(()))
}

#[derive(Deserialize)]
pub struct ChatBody {
    /// Free text; ignored when `action` is one of the quick actions.
    #[serde(default)]
    message: String,
    /// `explain_error`, `hint`, `complexity`, `similar` or `review`.
    action: Option<String>,
    /// The editor's current code, so answers see unsaved edits.
    code: Option<String>,
}

/// Streams an answer as server-sent events: `sources` (what it's grounded in), `assisted` (when this marked the
/// attempt), then `chunk`s of Markdown, then `done`, or `error`.
pub async fn chat(
    State(s): State<AppState>,
    Path(id): Path<String>,
    Json(body): Json<ChatBody>,
) -> ApiResult<Sse<impl Stream<Item = Result<Event, Infallible>>>> {
    let ai = ai(&s).await?;
    let (track, problem) = crate::routes::find(&s, &id)?;
    let prompt = match body.action.as_deref() {
        Some(a) => context::action_prompt(a).ok_or_else(|| ApiError::BadRequest(format!("unknown action {a:?}")))?.to_owned(),
        None if body.message.trim().is_empty() => return Err(ApiError::BadRequest("ask something".into())),
        None => body.message.trim().to_owned(),
    };

    // Help before a solve counts like a hint, so reviews and readiness stay honest.
    let attempt = store::current_attempt(&s.db, &id).await?;
    let assisted_now = attempt.solved_at.is_none() && !attempt.assisted;
    if attempt.solved_at.is_none() {
        store::mark_assisted(&s.db, attempt.id).await?;
    }

    let query_vector = if ai.ai.can_embed() {
        ai.ai.embed(vec![prompt.clone()]).await.ok().and_then(|mut v| v.pop())
    } else {
        None
    };
    let grounding = {
        let index = ai.index.read().await;
        context::build(&s.db, &s.catalog, &index, context::Ask { track, problem, code: body.code.clone(), query_vector })
            .await
            .map_err(|e| ApiError::Ai(ai.ai.redact(&e.to_string())))?
    };
    let history: Vec<(anneal_ai::Role, String)> = store::ai_messages(&s.db, &id)
        .await?
        .into_iter()
        .rev()
        .take(12)
        .rev()
        .map(|m| (if m.role == "user" { anneal_ai::Role::User } else { anneal_ai::Role::Assistant }, m.content))
        .collect();

    let shown = if body.action.is_some() { prompt.clone() } else { body.message.trim().to_owned() };
    store::add_ai_message(&s.db, &id, "user", &shown, body.action.as_deref(), &serde_json::json!([])).await?;
    let sources = serde_json::to_value(&grounding.sources).unwrap_or_default();

    let request = anneal_ai::Request {
        system: context::SYSTEM.to_owned(),
        history,
        prompt,
        context: grounding.documents,
        max_tokens: 2048,
    };
    let mut model = ai.ai.stream(request).await.map_err(|e| ApiError::Ai(ai.ai.redact(&format!("{e:#}"))))?;

    let (tx, rx) = mpsc::channel::<Event>(64);
    let db = s.db.clone();
    let action = body.action.clone();
    let scrub = ai.clone();
    tokio::spawn(async move {
        let _ = tx.send(Event::default().event("sources").data(sources.to_string())).await;
        if assisted_now {
            let _ = tx.send(Event::default().event("assisted").data("true")).await;
        }
        let mut answer = String::new();
        while let Some(chunk) = model.next().await {
            match chunk {
                Ok(text) => {
                    answer.push_str(&text);
                    let _ = tx.send(Event::default().event("chunk").data(serde_json::to_string(&text).unwrap_or_default())).await;
                }
                Err(e) => {
                    let _ = tx.send(Event::default().event("error").data(scrub.ai.redact(&format!("{e:#}")))).await;
                    break;
                }
            }
        }
        if !answer.is_empty()
            && let Err(e) = store::add_ai_message(&db, &id, "assistant", &answer, action.as_deref(), &sources).await
        {
            tracing::warn!(error = %e, "saving the assistant's answer failed");
        }
        let _ = tx.send(Event::default().event("done").data("")).await;
    });

    let stream = futures_util::stream::unfold(rx, |mut rx| async move { rx.recv().await.map(|e| (Ok(e), rx)) });
    Ok(Sse::new(stream).keep_alive(KeepAlive::default()))
}

// ---------------------------------------------------------------- similar problems

#[derive(Serialize)]
pub struct Similar {
    pub id: String,
    pub title: String,
    pub track: String,
    pub score: f32,
}

pub async fn similar(State(s): State<AppState>, Path(id): Path<String>) -> ApiResult<Json<Vec<Similar>>> {
    let ai = ai(&s).await?;
    crate::routes::find(&s, &id)?;
    let index = ai.index.read().await;
    Ok(Json(
        index
            .similar_problems(&id, 6)
            .into_iter()
            .filter_map(|(pid, score)| {
                let (t, p) = s.catalog.problem(&pid)?;
                Some(Similar { title: p.meta.title.clone(), track: t.code.clone(), id: pid, score })
            })
            .collect(),
    ))
}

// ---------------------------------------------------------------- patterns

pub use report::{get_patterns, refresh_patterns};
pub use settings::{delete_config, get_config, put_config};
