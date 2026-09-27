//! anneal's HTTP API. Content comes from files (loaded once at start-up),
//! progress lives in Postgres, and code runs through [`anneal_runner`].

mod activity;
pub mod auth;
mod error;
pub mod lsp;
mod progress;
pub mod reviews;
mod routes;
mod settings;
mod store;
mod views;

use std::path::Path;
use std::sync::Arc;

use anneal_content::Catalog;
use anneal_runner::Runner;
use axum::Router;
use axum::middleware;
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
    pub auth: auth::AuthConfig,
}

/// The API under `/api`. If `web_dist` is a built web app, it's served for every other path.
pub fn app(state: AppState, web_dist: Option<&Path>) -> Router {
    // Everything but health and the auth routes needs a session when auth is on.
    let protected = Router::new()
        .route("/activity", get(routes::activity))
        .route("/progress", get(routes::progress))
        .route("/stats", get(routes::stats))
        .route("/reviews", get(routes::reviews))
        .route("/problems/{id}/resolve", post(routes::resolve))
        .route("/problems/{id}/focus", post(routes::focus))
        .route("/tracks", get(routes::tracks))
        .route("/tracks/{track}", get(routes::track))
        .route("/problems/{id}", get(routes::problem))
        .route(
            "/problems/{id}/draft",
            put(routes::save_draft).delete(routes::reset),
        )
        .route("/problems/{id}/run", post(routes::run))
        .route("/problems/{id}/scratch", put(routes::save_scratch))
        .route("/problems/{id}/scratch/run", post(routes::run_scratch))
        .route("/problems/{id}/submit", post(routes::submit))
        .route("/problems/{id}/hints", post(routes::reveal_hint))
        .route("/problems/{id}/solution", post(routes::reveal_solution))
        .route("/settings", get(settings::get))
        .route("/settings/editor", put(settings::put_editor))
        .route("/settings/appearance", put(settings::put_appearance))
        .route("/lsp/{id}", get(routes::lsp))
        .route_layer(middleware::from_fn_with_state(state.clone(), auth::require));
    let api = Router::new()
        .route("/health", get(routes::health))
        .route("/auth/session", get(auth::session))
        .route("/auth/login", post(auth::login))
        .route("/auth/logout", post(auth::logout))
        .merge(protected)
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
