use axum::Json;
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use serde_json::json;

#[derive(Debug, thiserror::Error)]
pub enum ApiError {
    #[error("{0} not found")]
    NotFound(String),
    /// The problem is still a draft: it has no tests to run yet.
    #[error("{0} is a draft and can't be run yet")]
    NotReady(String),
    #[error("{0}")]
    BadRequest(String),
    #[error("{0}")]
    Busy(String),
    #[error(transparent)]
    Db(#[from] sqlx::Error),
    #[error(transparent)]
    Runner(#[from] anneal_runner::RunnerError),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, code) = match &self {
            ApiError::NotFound(_) => (StatusCode::NOT_FOUND, "not_found"),
            ApiError::NotReady(_) => (StatusCode::CONFLICT, "not_ready"),
            ApiError::BadRequest(_) => (StatusCode::BAD_REQUEST, "bad_request"),
            ApiError::Busy(_) => (StatusCode::TOO_MANY_REQUESTS, "busy"),
            ApiError::Db(_) | ApiError::Runner(_) => {
                (StatusCode::INTERNAL_SERVER_ERROR, "internal")
            }
        };
        if status.is_server_error() {
            tracing::error!(error = %self, "request failed");
        }
        (
            status,
            Json(json!({ "error": code, "message": self.to_string() })),
        )
            .into_response()
    }
}

pub type ApiResult<T> = Result<T, ApiError>;
