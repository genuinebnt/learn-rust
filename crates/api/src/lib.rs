//! anneal's HTTP API. Content comes from files (loaded once at start-up),
//! progress lives in Postgres, and code runs through [`anneal_runner`].

mod error;
pub mod lsp;
mod routes;
mod store;
mod views;

use std::path::Path;
use std::sync::Arc;

use anneal_content::Catalog;
use anneal_runner::Runner;
use axum::Router;
use axum::routing::{get, post, put};
use sqlx::PgPool;
use tower_http::services::{ServeDir, ServeFile};
use tower_http::trace::TraceLayer;

pub use error::ApiError;

pub static MIGRATOR: sqlx::migrate::Migrator = sqlx::migrate!("./migrations");

#[derive(Clone)]
pub struct AppState {
    pub catalog: Arc<Catalog>,
    pub runner: Arc<Runner>,
    pub db: PgPool,
    pub lsp: lsp::LspConfig,
}

/// The API under `/api`. If `web_dist` is a built web app, it's served for every other path.
pub fn app(state: AppState, web_dist: Option<&Path>) -> Router {
    let api = Router::new()
        .route("/health", get(routes::health))
        .route("/tracks", get(routes::tracks))
        .route("/tracks/{track}", get(routes::track))
        .route("/problems/{id}", get(routes::problem))
        .route(
            "/problems/{id}/draft",
            put(routes::save_draft).delete(routes::reset),
        )
        .route("/problems/{id}/run", post(routes::run))
        .route("/problems/{id}/submit", post(routes::submit))
        .route("/problems/{id}/hints", post(routes::reveal_hint))
        .route("/problems/{id}/solution", post(routes::reveal_solution))
        .route("/lsp/{id}", get(routes::lsp))
        .with_state(state);
    let mut router = Router::new().nest("/api", api);
    if let Some(dist) = web_dist.filter(|d| d.join("index.html").is_file()) {
        // Client-side routes all load index.html.
        router = router.fallback_service(
            ServeDir::new(dist).fallback(ServeFile::new(dist.join("index.html"))),
        );
    }
    router.layer(TraceLayer::new_for_http())
}
