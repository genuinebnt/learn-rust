//! Talking to the anneal web app from the CLI: `anneal course login` keeps a session, every `anneal course test` reports its run,
//! and `anneal course solutions` uploads each stage's solution diff (the reference is not in the public repo; the app serves
//! it only to the signed-in owner). Everything here is best effort: a learner without a login just works offline.
//!
//! HTTP goes through `curl` (always present on macOS and Linux), with the body on stdin so large uploads don't hit argv limits.

use std::collections::{BTreeMap, HashMap};
use std::fs;
use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Stdio};

use anyhow::{Context, bail};
use serde::{Deserialize, Serialize};
use similar::{ChangeTag, TextDiff};

const COOKIE: &str = "anneal_session";

#[derive(Debug, Serialize, Deserialize)]
struct Session {
    url: String,
    token: String,
}

fn session_path() -> Option<PathBuf> {
    let base = std::env::var_os("XDG_CONFIG_HOME").map(PathBuf::from).or_else(|| std::env::var_os("HOME").map(|h| PathBuf::from(h).join(".config")))?;
    Some(base.join("anneal").join("course-session.json"))
}

fn load_session() -> Option<Session> {
    serde_json::from_str(&fs::read_to_string(session_path()?).ok()?).ok()
}

/// One `curl` call. Returns (status, headers, body).
fn curl(method: &str, url: &str, token: Option<&str>, body: Option<&str>) -> anyhow::Result<(u16, String, String)> {
    let mut cmd = Command::new("curl");
    cmd.args(["-sS", "--max-time", "60", "-i", "-X", method, url, "-H", "content-type: application/json"]);
    if let Some(t) = token {
        cmd.args(["-H", &format!("Cookie: {COOKIE}={t}")]);
    }
    if body.is_some() {
        cmd.args(["--data-binary", "@-"]);
    }
    cmd.stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::piped());
    let mut child = cmd.spawn().context("running curl (is it installed?)")?;
    if let Some(mut stdin) = child.stdin.take()
        && let Some(b) = body
    {
        stdin.write_all(b.as_bytes())?;
    }
    let out = child.wait_with_output()?;
    if !out.status.success() {
        bail!("{}", String::from_utf8_lossy(&out.stderr).trim());
    }
    let text = String::from_utf8_lossy(&out.stdout).into_owned();
    // `-i` prints the headers first; a proxy's "100 Continue" block can come before the real one.
    let mut rest = text.as_str();
    loop {
        let (head, tail) = rest.split_once("\r\n\r\n").context("unexpected reply from the server")?;
        let status: u16 = head.split_whitespace().nth(1).and_then(|s| s.parse().ok()).context("no HTTP status")?;
        if status == 100 {
            rest = tail;
            continue;
        }
        return Ok((status, head.to_owned(), tail.to_owned()));
    }
}

/// `anneal course login <url>`: asks for the passphrase and keeps the session cookie in ~/.config/anneal.
pub fn login(url: &str) -> anyhow::Result<()> {
    let url = url.trim_end_matches('/').to_owned();
    let pass = match std::env::var("ANNEAL_PASSPHRASE") {
        Ok(p) if !p.is_empty() => p,
        _ => rpassword::prompt_password(format!("Passphrase for {url}: "))?,
    };
    let body = serde_json::json!({ "passphrase": pass }).to_string();
    let (status, head, text) = curl("POST", &format!("{url}/api/auth/login"), None, Some(&body))?;
    match status {
        200 | 204 => {}
        401 => bail!("wrong passphrase"),
        s => bail!("login failed ({s}): {text}"),
    }
    let token = head
        .lines()
        .filter(|l| l.to_ascii_lowercase().starts_with("set-cookie:"))
        .find_map(|l| l.split_once(&format!("{COOKIE}="))?.1.split(';').next().map(str::to_owned));
    let token = match token {
        Some(t) if !t.is_empty() => t,
        // Login is off on a local server: no cookie needed.
        _ if status == 204 => String::new(),
        _ => bail!("the server accepted the passphrase but sent no session"),
    };
    let path = session_path().context("no home directory")?;
    fs::create_dir_all(path.parent().unwrap())?;
    fs::write(&path, serde_json::to_string(&Session { url: url.clone(), token })? + "\n")?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&path, fs::Permissions::from_mode(0o600))?;
    }
    println!("Signed in to {url}. Runs from `anneal course test` and pushes are reported there now.");
    Ok(())
}

#[derive(Serialize)]
struct TestReport<'a> {
    name: &'a str,
    ok: bool,
    detail: &'a str,
}

/// Reports one stage run, if a session exists. Never fails the caller.
pub fn report_run(course: &str, stage: &str, tests: &[(String, bool, String)], problem: Option<&str>, commit: &str, ms: u64) {
    let Some(s) = load_session() else { return };
    let tests: Vec<TestReport> = tests.iter().map(|(n, ok, d)| TestReport { name: n.rsplit("::").next().unwrap_or(n), ok: *ok, detail: d }).collect();
    let body = serde_json::json!({ "stage_id": stage, "tests": tests, "problem": problem, "commit": commit, "duration_ms": ms }).to_string();
    match curl("POST", &format!("{}/api/courses/{course}/runs", s.url), Some(&s.token), Some(&body)) {
        Ok((200, ..)) => println!("\nReported to {}", s.url),
        Ok((401, ..)) => println!("\nNot reported: the session at {} expired. Run `anneal course login {}`.", s.url, s.url),
        Ok((404, ..)) => println!("\nNot reported: {} doesn't know stage {stage}. It may not be published there yet.", s.url),
        Ok((st, _, b)) => println!("\nNot reported ({st}): {}", b.trim()),
        Err(e) => println!("\nNot reported: {e}"),
    }
}

#[derive(Serialize)]
pub struct SolutionFile {
    path: String,
    lines: Vec<String>,
}

/// For each stage: the diff between the files rendered with the stage undone and done.
///
/// `render(cutoff)` returns every reference file rendered for "stages up to `cutoff` are done", keyed by path.
pub fn solution_diffs(ranks: &HashMap<String, usize>, render: &dyn Fn(usize) -> anyhow::Result<BTreeMap<String, String>>) -> anyhow::Result<BTreeMap<String, Vec<SolutionFile>>> {
    let mut by_rank: Vec<(&String, usize)> = ranks.iter().map(|(k, v)| (k, *v)).collect();
    by_rank.sort_by_key(|(_, r)| *r);
    let mut out = BTreeMap::new();
    let mut before = render(0)?;
    for (id, rank) in by_rank {
        let after = render(rank)?;
        let mut files = Vec::new();
        for (path, new) in &after {
            let old = before.get(path).map(String::as_str).unwrap_or("");
            if old == new {
                continue;
            }
            let diff = TextDiff::from_lines(old, new);
            let mut lines = Vec::new();
            for (gi, group) in diff.grouped_ops(3).iter().enumerate() {
                if gi > 0 {
                    lines.push(" ⋯".to_owned());
                }
                for op in group {
                    for ch in diff.iter_changes(op) {
                        let sign = match ch.tag() {
                            ChangeTag::Equal => ' ',
                            ChangeTag::Insert => '+',
                            ChangeTag::Delete => '-',
                        };
                        lines.push(format!("{sign}{}", ch.value().trim_end_matches('\n')));
                    }
                }
            }
            files.push(SolutionFile { path: path.clone(), lines });
        }
        out.insert(id.clone(), files);
        before = after;
    }
    Ok(out)
}

/// Uploads `stages` (stage id -> files) to the signed-in app.
pub fn push_solutions(course: &str, stages: &BTreeMap<String, Vec<SolutionFile>>, only: Option<&[String]>) -> anyhow::Result<()> {
    let s = load_session().context("not signed in: run `anneal course login <url>` first")?;
    let mut sel: BTreeMap<&String, &Vec<SolutionFile>> = BTreeMap::new();
    for (k, v) in stages {
        if v.is_empty() || only.is_some_and(|o| !o.contains(k)) {
            continue;
        }
        sel.insert(k, v);
    }
    // The server rejects ids it doesn't publish; upload one stage at a time and report which were refused.
    let (mut ok, mut skipped) = (0, Vec::new());
    for (id, files) in sel {
        let body = serde_json::json!({ "stages": { id: files } }).to_string();
        match curl("PUT", &format!("{}/api/courses/{course}/solutions", s.url), Some(&s.token), Some(&body))? {
            (200, ..) => ok += 1,
            (401, ..) => bail!("the session expired: run `anneal course login {}`", s.url),
            (404, ..) => skipped.push(id.clone()),
            (st, _, b) => bail!("uploading {id} failed ({st}): {}", b.trim()),
        }
    }
    println!("Uploaded {ok} stage solutions to {}.", s.url);
    if !skipped.is_empty() {
        println!("Skipped {} the server doesn't publish yet: {}", skipped.len(), skipped.join(", "));
    }
    Ok(())
}
