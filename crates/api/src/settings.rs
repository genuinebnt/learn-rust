//! User settings: the editor, and the app's appearance.

use axum::Json;
use axum::extract::State;
use serde::{Deserialize, Serialize};
use sqlx::types::Json as Jsonb;

use crate::AppState;
use crate::error::{ApiError, ApiResult};

/// Font families the web app knows how to load. `system` is the OS monospace font.
pub const FONT_FAMILIES: &[&str] = &["JetBrains Mono", "Fira Code", "IBM Plex Mono", "Source Code Pro", "Roboto Mono", "system"];
pub const FONT_SIZES: std::ops::RangeInclusive<u8> = 10..=24;
/// Accent colours the web app has palettes for. Copper is the design's own.
pub const ACCENTS: &[&str] = &["copper", "rose", "sky", "teal"];

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

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AppearanceSettings {
    pub accent: String,
}

impl Default for AppearanceSettings {
    fn default() -> Self {
        AppearanceSettings { accent: "copper".into() }
    }
}

#[derive(Debug, Serialize)]
pub struct Settings {
    pub editor: EditorSettings,
    pub appearance: AppearanceSettings,
    pub accents: &'static [&'static str],
    /// What the editor settings may be set to.
    pub font_families: &'static [&'static str],
    pub font_sizes: [u8; 2],
}

pub async fn get(State(s): State<AppState>) -> ApiResult<Json<Settings>> {
    let editor: Option<Jsonb<EditorSettings>> = sqlx::query_scalar("SELECT value FROM settings WHERE key = 'editor'")
        .fetch_optional(&s.db)
        .await?;
    let appearance: Option<Jsonb<AppearanceSettings>> = sqlx::query_scalar("SELECT value FROM settings WHERE key = 'appearance'")
        .fetch_optional(&s.db)
        .await?;
    Ok(Json(Settings {
        editor: editor.map(|j| j.0).unwrap_or_default(),
        appearance: appearance.map(|j| j.0).unwrap_or_default(),
        accents: ACCENTS,
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
    store(&s, "editor", &e).await?;
    Ok(Json(e))
}

pub async fn put_appearance(State(s): State<AppState>, Json(a): Json<AppearanceSettings>) -> ApiResult<Json<AppearanceSettings>> {
    if !ACCENTS.contains(&a.accent.as_str()) {
        return Err(ApiError::BadRequest(format!("accent must be one of {}", ACCENTS.join(", "))));
    }
    store(&s, "appearance", &a).await?;
    Ok(Json(a))
}

async fn store<T: Serialize>(s: &AppState, key: &str, value: &T) -> ApiResult<()> {
    sqlx::query(
        "INSERT INTO settings (key, value) VALUES ($1, $2)
         ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = now()",
    )
    .bind(key)
    .bind(Jsonb(value))
    .execute(&s.db)
    .await?;
    Ok(())
}
