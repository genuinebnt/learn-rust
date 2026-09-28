//! The assistant's provider and key, saved from the app (the AI tab's settings). The key stays on the server: the
//! browser only ever gets the provider, the model and the key's last four characters. A saved key wins over one in
//! the environment; removing it falls back to the environment.

use std::time::Duration;

use anneal_ai::{Config, Provider};
use axum::Json;
use axum::extract::State;
use serde::{Deserialize, Serialize};
use sqlx::PgPool;
use sqlx::types::Json as Jsonb;

use super::AiState;
use crate::AppState;
use crate::error::{ApiError, ApiResult};

#[derive(Clone, Serialize, Deserialize)]
pub struct Saved {
    provider: Provider,
    api_key: String,
    #[serde(default)]
    model: Option<String>,
}

impl Saved {
    pub fn config(&self) -> Config {
        Config::single(self.provider, self.api_key.clone(), self.model.clone())
    }
}

pub async fn load(db: &PgPool) -> sqlx::Result<Option<Saved>> {
    let row: Option<Jsonb<Saved>> = sqlx::query_scalar("SELECT value FROM settings WHERE key = 'ai'").fetch_optional(db).await?;
    Ok(row.map(|j| j.0))
}

/// What the browser may know about the configuration.
#[derive(Serialize)]
pub struct View {
    /// `settings`, `environment`, or `none`.
    source: &'static str,
    provider: Option<Provider>,
    model: Option<String>,
    /// The key's last four characters, e.g. `…x9Qk`.
    key_hint: Option<String>,
}

fn hint(key: &str) -> String {
    let tail: String = key.chars().rev().take(4).collect::<Vec<_>>().into_iter().rev().collect();
    format!("…{tail}")
}

async fn view(db: &PgPool) -> ApiResult<View> {
    if let Some(s) = load(db).await? {
        return Ok(View { source: "settings", provider: Some(s.provider), model: s.model.clone(), key_hint: Some(hint(&s.api_key)) });
    }
    Ok(match Config::from_env() {
        Ok(Some(c)) => View { source: "environment", provider: Some(c.provider), model: c.model.clone(), key_hint: Some(hint(&c.api_key)) },
        _ => View { source: "none", provider: None, model: None, key_hint: None },
    })
}

pub async fn get_config(State(s): State<AppState>) -> ApiResult<Json<View>> {
    Ok(Json(view(&s.db).await?))
}

#[derive(Deserialize)]
pub struct PutConfig {
    provider: Provider,
    /// Leave out to keep the saved key (e.g. to change only the model).
    #[serde(default)]
    api_key: Option<String>,
    #[serde(default)]
    model: Option<String>,
}

/// Checks the key with a tiny request, then saves it and switches the assistant over.
pub async fn put_config(State(s): State<AppState>, Json(body): Json<PutConfig>) -> ApiResult<Json<View>> {
    let api_key = match body.api_key.map(|k| k.trim().to_owned()).filter(|k| !k.is_empty()) {
        Some(k) => k,
        None => match load(&s.db).await? {
            Some(saved) if saved.provider == body.provider => saved.api_key,
            _ => return Err(ApiError::BadRequest("paste an API key for this provider".into())),
        },
    };
    let model = body.model.map(|m| m.trim().to_owned()).filter(|m| !m.is_empty());
    let saved = Saved { provider: body.provider, api_key, model };
    let ai = anneal_ai::Ai::new(saved.config()).map_err(|e| ApiError::BadRequest(format!("{e:#}")))?;
    match tokio::time::timeout(Duration::from_secs(30), ai.check()).await {
        Err(_) => return Err(ApiError::BadRequest("the provider didn't answer within 30 s; try again".into())),
        Ok(Err(e)) => return Err(ApiError::BadRequest(format!("that key didn't work: {}", ai.redact(&format!("{e:#}"))))),
        Ok(Ok(())) => {}
    }
    sqlx::query(
        "INSERT INTO settings (key, value) VALUES ('ai', $1)
         ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()",
    )
    .bind(Jsonb(&saved))
    .execute(&s.db)
    .await?;
    tracing::info!(provider = ?saved.provider, model = %ai.info.model, "AI assistant configured from the settings");
    s.ai.set(Some(AiState::new(ai))).await;
    super::refresh_in_background(&s);
    Ok(Json(view(&s.db).await?))
}

/// Forgets the saved key; the assistant falls back to the environment's key, or turns off.
pub async fn delete_config(State(s): State<AppState>) -> ApiResult<Json<View>> {
    sqlx::query("DELETE FROM settings WHERE key = 'ai'").execute(&s.db).await?;
    let ai = anneal_ai::Ai::from_env().map_err(|e| ApiError::BadRequest(format!("{e:#}")))?.map(AiState::new);
    let on = ai.is_some();
    s.ai.set(ai).await;
    if on {
        super::refresh_in_background(&s);
    }
    Ok(Json(view(&s.db).await?))
}
