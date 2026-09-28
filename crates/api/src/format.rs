//! `POST /api/format`: rustfmt for the editor (⌘S, ⇧⌥F, and the optional format-on-pause). rustfmt only parses
//! and prints the code, so it runs here rather than in the sandbox.

use std::process::Stdio;
use std::time::Duration;

use axum::Json;
use serde::{Deserialize, Serialize};
use tokio::io::AsyncWriteExt;
use tokio::process::Command;

use crate::error::{ApiError, ApiResult};

const MAX_BYTES: usize = 256 * 1024;

#[derive(Deserialize)]
pub struct FormatBody {
    pub code: String,
}

#[derive(Serialize)]
pub struct Formatted {
    pub code: String,
}

pub async fn format(Json(body): Json<FormatBody>) -> ApiResult<Json<Formatted>> {
    if body.code.len() > MAX_BYTES {
        return Err(ApiError::BadRequest("too much code to format".into()));
    }
    let binary = std::env::var("ANNEAL_RUSTFMT").unwrap_or_else(|_| "rustfmt".into());
    let run = async {
        let mut child = Command::new(&binary)
            // Problem crates are edition 2021; rustfmt reads stdin and prints to stdout.
            .args(["--edition", "2021", "--emit", "stdout", "--quiet"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .kill_on_drop(true)
            .spawn()?;
        let mut stdin = child.stdin.take().expect("stdin is piped");
        stdin.write_all(body.code.as_bytes()).await?;
        drop(stdin);
        child.wait_with_output().await
    };
    let out = tokio::time::timeout(Duration::from_secs(5), run)
        .await
        .map_err(|_| ApiError::Busy("rustfmt took too long".into()))?
        .map_err(|e| ApiError::Busy(format!("rustfmt isn't available: {e}")))?;
    if !out.status.success() {
        // rustfmt's first line names the parse error, e.g. "error: expected `;`, found `}`".
        let stderr = String::from_utf8_lossy(&out.stderr);
        let first = stderr.lines().find(|l| !l.trim().is_empty()).unwrap_or("rustfmt couldn't parse the code");
        return Err(ApiError::BadRequest(first.trim().to_owned()));
    }
    let code = String::from_utf8(out.stdout).map_err(|_| ApiError::BadRequest("rustfmt printed invalid UTF-8".into()))?;
    Ok(Json(Formatted { code }))
}
