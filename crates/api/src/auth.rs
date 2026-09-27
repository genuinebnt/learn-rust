//! Single-user auth: one passphrase (an argon2 hash from the environment) and cookie sessions.
//!
//! With no passphrase configured, auth is off and every route is open; `main` only allows that
//! on a loopback address.

use std::sync::Arc;
use std::time::{Duration, Instant};

use argon2::password_hash::rand_core::{OsRng, RngCore};
use argon2::{Argon2, PasswordHash, PasswordVerifier};
use axum::Json;
use axum::extract::{Request, State};
use axum::http::header::{COOKIE, SET_COOKIE};
use axum::http::{HeaderMap, HeaderValue, StatusCode};
use axum::middleware::Next;
use axum::response::{IntoResponse, Response};
use base64::Engine;
use base64::engine::general_purpose::URL_SAFE_NO_PAD;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use tokio::sync::Mutex;

use crate::AppState;
use crate::error::{ApiError, ApiResult};

const COOKIE_NAME: &str = "anneal_session";
const SESSION_DAYS: i64 = 30;
/// Consecutive wrong passphrases before logins pause.
const MAX_FAILURES: u32 = 5;
const LOCKOUT: Duration = Duration::from_secs(60);

#[derive(Clone)]
pub struct AuthConfig {
    /// argon2 PHC string; `None` turns auth off.
    passphrase_hash: Option<Arc<str>>,
    /// Adds `Secure` to the cookie; set when served over HTTPS.
    secure_cookie: bool,
    failures: Arc<Mutex<Failures>>,
}

#[derive(Default)]
struct Failures {
    count: u32,
    locked_until: Option<Instant>,
}

impl AuthConfig {
    pub fn disabled() -> Self {
        AuthConfig { passphrase_hash: None, secure_cookie: false, failures: Arc::default() }
    }

    /// Fails if `hash` isn't a PHC string, e.g. from `anneal passphrase`.
    pub fn new(hash: &str, secure_cookie: bool) -> Result<Self, argon2::password_hash::Error> {
        PasswordHash::new(hash)?;
        Ok(AuthConfig { passphrase_hash: Some(hash.into()), secure_cookie, failures: Arc::default() })
    }

    pub fn required(&self) -> bool {
        self.passphrase_hash.is_some()
    }
}

#[derive(Serialize)]
pub struct SessionView {
    pub required: bool,
    pub authenticated: bool,
}

#[derive(Deserialize)]
pub struct LoginBody {
    passphrase: String,
}

fn session_token(headers: &HeaderMap) -> Option<&str> {
    headers
        .get_all(COOKIE)
        .iter()
        .filter_map(|v| v.to_str().ok())
        .flat_map(|v| v.split(';'))
        .find_map(|kv| kv.trim().strip_prefix(COOKIE_NAME)?.strip_prefix('='))
}

fn digest(token: &str) -> Vec<u8> {
    Sha256::digest(token.as_bytes()).to_vec()
}

async fn valid_session(s: &AppState, headers: &HeaderMap) -> ApiResult<bool> {
    let Some(token) = session_token(headers) else { return Ok(false) };
    let found: Option<i32> = sqlx::query_scalar("SELECT 1 FROM sessions WHERE token_hash = $1 AND expires_at > now()")
        .bind(digest(token))
        .fetch_optional(&s.db)
        .await?;
    Ok(found.is_some())
}

/// Route layer for everything except health and the auth routes themselves.
pub async fn require(State(s): State<AppState>, req: Request, next: Next) -> Response {
    if !s.auth.required() {
        return next.run(req).await;
    }
    match valid_session(&s, req.headers()).await {
        Ok(true) => next.run(req).await,
        Ok(false) => ApiError::Unauthorized.into_response(),
        Err(e) => e.into_response(),
    }
}

pub async fn session(State(s): State<AppState>, headers: HeaderMap) -> ApiResult<Json<SessionView>> {
    let required = s.auth.required();
    let authenticated = !required || valid_session(&s, &headers).await?;
    Ok(Json(SessionView { required, authenticated }))
}

fn cookie(value: &str, max_age: i64, secure: bool) -> HeaderValue {
    let secure = if secure { "; Secure" } else { "" };
    HeaderValue::from_str(&format!("{COOKIE_NAME}={value}; Path=/; HttpOnly; SameSite=Strict; Max-Age={max_age}{secure}"))
        .expect("cookie is ASCII")
}

pub async fn login(State(s): State<AppState>, Json(body): Json<LoginBody>) -> ApiResult<Response> {
    let Some(hash) = s.auth.passphrase_hash.clone() else {
        return Ok(StatusCode::NO_CONTENT.into_response());
    };
    {
        let f = s.auth.failures.lock().await;
        if f.locked_until.is_some_and(|t| Instant::now() < t) {
            return Err(ApiError::Busy("too many wrong passphrases; try again in a minute".into()));
        }
    }
    // argon2 is deliberately slow; keep it off the async workers.
    let ok = tokio::task::spawn_blocking(move || {
        let parsed = PasswordHash::new(&hash).expect("checked at start-up");
        Argon2::default().verify_password(body.passphrase.as_bytes(), &parsed).is_ok()
    })
    .await
    .unwrap_or(false);

    let mut f = s.auth.failures.lock().await;
    if !ok {
        f.count += 1;
        if f.count >= MAX_FAILURES {
            f.count = 0;
            f.locked_until = Some(Instant::now() + LOCKOUT);
        }
        return Err(ApiError::WrongPassphrase);
    }
    *f = Failures::default();
    drop(f);

    let mut bytes = [0u8; 32];
    OsRng.fill_bytes(&mut bytes);
    let token = URL_SAFE_NO_PAD.encode(bytes);
    sqlx::query("INSERT INTO sessions (token_hash, expires_at) VALUES ($1, now() + make_interval(days => $2))")
        .bind(digest(&token))
        .bind(SESSION_DAYS as i32)
        .execute(&s.db)
        .await?;
    sqlx::query("DELETE FROM sessions WHERE expires_at <= now()").execute(&s.db).await?;
    let mut res = StatusCode::NO_CONTENT.into_response();
    res.headers_mut().insert(SET_COOKIE, cookie(&token, SESSION_DAYS * 86_400, s.auth.secure_cookie));
    Ok(res)
}

pub async fn logout(State(s): State<AppState>, headers: HeaderMap) -> ApiResult<Response> {
    if let Some(token) = session_token(&headers) {
        sqlx::query("DELETE FROM sessions WHERE token_hash = $1").bind(digest(token)).execute(&s.db).await?;
    }
    let mut res = StatusCode::NO_CONTENT.into_response();
    res.headers_mut().insert(SET_COOKIE, cookie("", 0, s.auth.secure_cookie));
    Ok(res)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finds_the_session_cookie_among_others() {
        let mut h = HeaderMap::new();
        h.insert(COOKIE, HeaderValue::from_static("theme=dark; anneal_session=abc123; x=1"));
        assert_eq!(session_token(&h), Some("abc123"));
        h.insert(COOKIE, HeaderValue::from_static("anneal_sessionx=nope"));
        assert_eq!(session_token(&h), None);
    }
}
