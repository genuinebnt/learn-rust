//! User settings. Only the editor has any so far.

use axum::Json;
use axum::extract::State;
use serde::{Deserialize, Serialize};
use sqlx::types::Json as Jsonb;

use crate::AppState;
use crate::error::{ApiError, ApiResult};

/// Font families the web app knows how to load. `system` is the OS monospace font.
pub const FONT_FAMILIES: &[&str] = &["JetBrains Mono", "Fira Code", "IBM Plex Mono", "Source Code Pro", "Roboto Mono", "system"];
pub const FONT_SIZES: std::ops::RangeInclusive<u8> = 10..=24;

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EditorSettings {
    pub font_size: u8,
    pub font_family: String,
    /// Vim keybindings; `jk` / `kj` leave insert mode.
    #[serde(default)]
    pub vim: bool,
}

impl Default for EditorSettings {
    fn default() -> Self {
        EditorSettings { font_size: 13, font_family: "JetBrains Mono".into(), vim: false }
    }
}

#[derive(Debug, Serialize)]
pub struct Settings {
    pub editor: EditorSettings,
    /// What the editor settings may be set to.
    pub font_families: &'static [&'static str],
    pub font_sizes: [u8; 2],
}

pub async fn get(State(s): State<AppState>) -> ApiResult<Json<Settings>> {
    let stored: Option<Jsonb<EditorSettings>> = sqlx::query_scalar("SELECT value FROM settings WHERE key = 'editor'")
        .fetch_optional(&s.db)
        .await?;
    Ok(Json(Settings {
        editor: stored.map(|j| j.0).unwrap_or_default(),
        font_families: FONT_FAMILIES,
        font_sizes: [*FONT_SIZES.start(), *FONT_SIZES.end()],
    }))
}

pub async fn put_editor(State(s): State<AppState>, Json(e): Json<EditorSettings>) -> ApiResult<Json<EditorSettings>> {
    if !FONT_SIZES.contains(&e.font_size) {
        return Err(ApiError::BadRequest(format!("font_size must be {}–{}", FONT_SIZES.start(), FONT_SIZES.end())));
    }
    if !FONT_FAMILIES.contains(&e.font_family.as_str()) {
        return Err(ApiError::BadRequest(format!("font_family must be one of {}", FONT_FAMILIES.join(", "))));
    }
    sqlx::query(
        "INSERT INTO settings (key, value) VALUES ('editor', $1)
         ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()",
    )
    .bind(Jsonb(&e))
    .execute(&s.db)
    .await?;
    Ok(Json(e))
}
