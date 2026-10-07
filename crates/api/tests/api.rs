//! Each test gets its own database from `#[sqlx::test]` (needs the compose Postgres)
//! and runs code with host cargo.

use std::path::Path;
use std::sync::Arc;

use anneal_api::auth::AuthConfig;
use anneal_api::lsp::LspConfig;
use anneal_api::{AppState, app};
use anneal_content::Catalog;
use anneal_runner::{Runner, RunnerConfig, Sandbox};
use axum::Router;
use axum::body::Body;
use axum::http::{Method, Request, StatusCode};
use http_body_util::BodyExt;
use serde_json::{Value, json};
use sqlx::PgPool;
use tower::ServiceExt;

const NDT: &str = "d9-network-delay-time";

const SENTINEL_BUG: &str = r#"use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn network_delay(times: &[(usize, usize, u32)], n: usize, k: usize) -> Option<u32> {
    let mut adj = vec![Vec::new(); n + 1];
    for &(u, v, w) in times {
        adj[u].push((v, w));
    }
    let mut dist = vec![u32::MAX; n + 1];
    let mut heap = BinaryHeap::new();
    dist[k] = 0;
    heap.push(Reverse((0, k)));
    while let Some(Reverse((d, u))) = heap.pop() {
        if d > dist[u] { continue; }
        for &(v, w) in &adj[u] {
            let nd = d + w;
            if nd < dist[v] {
                dist[v] = nd;
                heap.push(Reverse((nd, v)));
            }
        }
    }
    dist[1..].iter().copied().max()
}
"#;

/// D9's problem ids in track order, from the content the app serves: counts and positions follow the content
/// instead of being pinned, since the track keeps growing.
fn d9_ids() -> Vec<String> {
    let loaded = Catalog::load(&content_root()).expect("content");
    loaded.catalog.track("D9").expect("D9").problems.iter().map(|p| p.id.clone()).collect()
}

fn fixtures() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../content/fixtures")
}

fn copy_dir(from: &Path, to: &Path) {
    std::fs::create_dir_all(to).unwrap();
    for entry in std::fs::read_dir(from).unwrap() {
        let entry = entry.unwrap();
        let target = to.join(entry.file_name());
        if entry.file_type().unwrap().is_dir() {
            copy_dir(&entry.path(), &target);
        } else {
            std::fs::copy(entry.path(), target).unwrap();
        }
    }
}

/// The content the API tests run against, `crates/content/fixtures/runnable`: a two-problem slice of the old D9 Graphs track
/// and one L2 Borrowing problem, which the tests solve in Rust. (The DSA section's real problems are LeetCode links.)
fn content_root() -> std::path::PathBuf {
    fixtures().join("runnable")
}

fn test_app(db: PgPool) -> Router {
    test_app_with(db, &content_root())
}

fn test_app_with(db: PgPool, content: &Path) -> Router {
    test_app_auth(db, content, AuthConfig::disabled())
}

fn test_app_auth(db: PgPool, content: &Path, auth: AuthConfig) -> Router {
    test_app_full(db, content, auth, None)
}

fn test_app_full(db: PgPool, content: &Path, auth: AuthConfig, web_dist: Option<&Path>) -> Router {
    let loaded = Catalog::load(content).expect("content");
    assert!(loaded.issues.is_empty(), "{:?}", loaded.issues);
    let runner = Runner::new(RunnerConfig::new(
        Sandbox::Host,
        Path::new(env!("CARGO_TARGET_TMPDIR")).join("anneal-api"),
    ));
    app(
        AppState {
            catalog: Arc::new(loaded.catalog),
            runner: Arc::new(runner),
            db,
            lsp: LspConfig::new(
                "rust-analyzer",
                Path::new(env!("CARGO_TARGET_TMPDIR")).join("anneal-api"),
            ),
            auth,
        },
        web_dist,
    )
}

async fn call(
    app: &Router,
    method: Method,
    path: &str,
    body: Option<Value>,
) -> (StatusCode, Value) {
    let req = Request::builder()
        .method(method)
        .uri(path)
        .header("content-type", "application/json");
    let req = req
        .body(body.map_or_else(Body::empty, |b| Body::from(b.to_string())))
        .unwrap();
    let res = app.clone().oneshot(req).await.unwrap();
    let status = res.status();
    let bytes = res.into_body().collect().await.unwrap().to_bytes();
    (
        status,
        if bytes.is_empty() {
            Value::Null
        } else {
            serde_json::from_slice(&bytes).unwrap()
        },
    )
}

fn solution() -> String {
    std::fs::read_to_string(content_root().join("tracks/d9-graphs/problems/network-delay-time/solution.rs")).unwrap()
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn lists_tracks_with_stage_counts(db: PgPool) {
    let app = test_app(db);
    let (status, body) = call(&app, Method::GET, "/api/tracks", None).await;
    assert_eq!(status, StatusCode::OK);
    let d9 = body
        .as_array()
        .unwrap()
        .iter()
        .find(|t| t["code"] == "D9")
        .unwrap();
    assert_eq!(
        (
            d9["total"].as_u64(),
            d9["ready"].as_u64(),
            d9["solved"].as_u64()
        ),
        (Some(d9_ids().len() as u64), Some(d9_ids().len() as u64), Some(0))
    );
    assert_eq!(d9["readiness"], 0.0);
    assert_eq!(d9["stages"][0]["band"], "easy");
    assert_eq!(
        d9["stages"].as_array().unwrap().last().unwrap()["band"],
        "medium"
    );
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn new_problem_has_everything_locked_and_no_hidden_tests(db: PgPool) {
    let app = test_app(db);
    let (status, p) = call(&app, Method::GET, &format!("/api/problems/{NDT}"), None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(p["stage"]["name"], "Shortest paths");
    assert_eq!(
        (p["position"].as_u64(), p["count"].as_u64()),
        (Some(d9_ids().iter().position(|id| id == NDT).unwrap() as u64 + 1), Some(d9_ids().len() as u64))
    );
    assert_eq!(p["hints"]["total"], 3);
    assert_eq!(p["hints"]["revealed"], json!([]));
    assert_eq!(
        p["hints"]["locked"],
        json!(["approach", "rust", "edge case"])
    );
    assert_eq!(
        p["solution"],
        json!({ "unlocked": false, "code": null, "notes": null })
    );
    assert_eq!(p["attempt"]["started"], false);
    assert!(!p.to_string().contains("dense_n100"), "hidden tests leaked");
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn run_then_submit_redacts_hidden_tests(db: PgPool) {
    let app = test_app(db);
    let (status, out) = call(
        &app,
        Method::POST,
        &format!("/api/problems/{NDT}/run"),
        Some(json!({ "code": SENTINEL_BUG })),
    )
    .await;
    assert_eq!(status, StatusCode::OK, "{out}");
    assert_eq!(
        (out["run"]["passed"].as_u64(), out["run"]["total"].as_u64()),
        (Some(4), Some(5))
    );
    assert_eq!(out["attempt"]["started"], true);

    let (_, out) = call(
        &app,
        Method::POST,
        &format!("/api/problems/{NDT}/submit"),
        Some(json!({ "code": SENTINEL_BUG })),
    )
    .await;
    assert_eq!(
        (out["run"]["passed"].as_u64(), out["run"]["total"].as_u64()),
        (Some(9), Some(14))
    );
    let hidden = out["run"]["tests"]
        .as_array()
        .unwrap()
        .iter()
        .find(|t| t["suite"] == "hidden" && t["outcome"] != "passed")
        .unwrap();
    assert_eq!(
        hidden["check"],
        json!({ "input": "withheld", "expected": "withheld", "got": "wrong answer" })
    );
    assert_eq!(hidden["panic"], Value::Null);
    assert_eq!(out["attempt"]["solved"], false);
    assert_eq!(out["solution"]["unlocked"], false);

    // Both runs are in the timeline, with the code, and the buffer was autosaved.
    let (_, p) = call(&app, Method::GET, &format!("/api/problems/{NDT}"), None).await;
    let kinds: Vec<&str> = p["runs"]
        .as_array()
        .unwrap()
        .iter()
        .map(|r| r["kind"].as_str().unwrap())
        .collect();
    assert_eq!(kinds, ["run", "submit"]);
    assert_eq!(p["draft"], SENTINEL_BUG);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn passing_submit_solves_and_unlocks_the_solution(db: PgPool) {
    let app = test_app(db);
    let (_, before) = call(&app, Method::GET, &format!("/api/problems/{NDT}"), None).await;
    assert!(before["hidden_tests"].is_null(), "hidden tests stay hidden until solved");
    let (_, out) = call(
        &app,
        Method::POST,
        &format!("/api/problems/{NDT}/submit"),
        Some(json!({ "code": solution() })),
    )
    .await;
    assert_eq!(out["run"]["status"], "passed", "{out}");
    assert_eq!(
        (
            out["attempt"]["solved"].as_bool(),
            out["attempt"]["assisted"].as_bool()
        ),
        (Some(true), Some(false))
    );
    assert_eq!(out["solution"]["unlocked"], true);
    assert!(
        out["solution"]["code"]
            .as_str()
            .unwrap()
            .contains("then_some")
    );

    let (_, t) = call(&app, Method::GET, "/api/tracks/d9", None).await;
    let p = t["problems"]
        .as_array()
        .unwrap()
        .iter()
        .find(|p| p["id"] == NDT)
        .unwrap();
    assert_eq!(p["progress"], "solved");
    assert_eq!(t["solved"], 1);

    // Solved: the hidden test file is readable, and runs show hidden tests in full.
    let (_, after) = call(&app, Method::GET, &format!("/api/problems/{NDT}"), None).await;
    assert!(after["hidden_tests"].as_str().unwrap().contains("fn dense_n100"));
    let (_, bad) = call(&app, Method::POST, &format!("/api/problems/{NDT}/submit"), Some(json!({ "code": SENTINEL_BUG }))).await;
    let hidden = bad["run"]["tests"].as_array().unwrap().iter().find(|t| t["suite"] == "hidden").unwrap();
    assert_ne!(hidden["check"]["input"], "withheld", "{hidden}");
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn hints_reveal_one_at_a_time_and_mark_assisted(db: PgPool) {
    let app = test_app(db);
    let path = format!("/api/problems/{NDT}/hints");
    let (_, p) = call(&app, Method::POST, &path, None).await;
    assert_eq!(p["hints"]["revealed"].as_array().unwrap().len(), 1);
    assert_eq!(p["hints"]["revealed"][0]["kind"], "approach");
    assert_eq!(p["attempt"]["assisted"], true);
    for _ in 0..4 {
        call(&app, Method::POST, &path, None).await;
    }
    let (_, p) = call(&app, Method::GET, &format!("/api/problems/{NDT}"), None).await;
    assert_eq!(p["hints"]["revealed"].as_array().unwrap().len(), 3);
    assert_eq!(p["hints"]["locked"], json!([]));

    // An assisted solve still unlocks the solution, and stays assisted.
    let (_, out) = call(
        &app,
        Method::POST,
        &format!("/api/problems/{NDT}/submit"),
        Some(json!({ "code": solution() })),
    )
    .await;
    assert_eq!(
        (
            out["attempt"]["solved"].as_bool(),
            out["attempt"]["assisted"].as_bool()
        ),
        (Some(true), Some(true))
    );
    let (_, t) = call(&app, Method::GET, "/api/tracks/d9", None).await;
    assert_eq!(
        t["problems"]
            .as_array()
            .unwrap()
            .iter()
            .find(|p| p["id"] == NDT)
            .unwrap()["progress"],
        "assisted"
    );
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn reveal_anyway_unlocks_and_marks_assisted(db: PgPool) {
    let app = test_app(db);
    let (_, p) = call(
        &app,
        Method::POST,
        &format!("/api/problems/{NDT}/solution"),
        None,
    )
    .await;
    assert_eq!(p["solution"]["unlocked"], true);
    assert_eq!(p["solution"]["notes"]["time"], "O(E log E)");
    assert_eq!(p["attempt"]["assisted"], true);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn drafts_save_and_reset(db: PgPool) {
    let app = test_app(db);
    let (status, _) = call(
        &app,
        Method::PUT,
        &format!("/api/problems/{NDT}/draft"),
        Some(json!({ "code": "// wip" })),
    )
    .await;
    assert_eq!(status, StatusCode::NO_CONTENT);
    let (_, p) = call(&app, Method::GET, &format!("/api/problems/{NDT}"), None).await;
    assert_eq!(p["draft"], "// wip");
    let (_, p) = call(
        &app,
        Method::DELETE,
        &format!("/api/problems/{NDT}/draft"),
        None,
    )
    .await;
    assert_eq!(p["draft"], Value::Null);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn draft_problems_and_unknown_ids_are_refused(db: PgPool) {
    // All shipped problems are ready, so use a one-problem catalog with a draft.
    let dir = tempfile::tempdir().unwrap();
    let track = dir.path().join("tracks/d99-fixture");
    std::fs::create_dir_all(track.join("problems/only-draft")).unwrap();
    std::fs::write(
        track.join("track.toml"),
        "code = \"D99\"\nname = \"Fixture\"\nsection = \"D\"\ntier = \"core\"\norder = 99\nsummary = \"x\"\n\n[[stages]]\nslug = \"s\"\nname = \"S\"\nband = \"easy\"\n",
    )
    .unwrap();
    std::fs::write(
        track.join("problems/only-draft/problem.toml"),
        "slug = \"only-draft\"\ntitle = \"Draft\"\nmode = \"write\"\nlevel = \"easy\"\nstage = \"s\"\norder = 1\nstatus = \"draft\"\ntags = []\n",
    )
    .unwrap();
    let app = test_app_with(db, dir.path());
    let (status, body) = call(
        &app,
        Method::POST,
        "/api/problems/d99-only-draft/run",
        Some(json!({ "code": "" })),
    )
    .await;
    assert_eq!(status, StatusCode::CONFLICT);
    assert_eq!(body["error"], "not_ready");
    let (status, _) = call(&app, Method::GET, "/api/problems/nope", None).await;
    assert_eq!(status, StatusCode::NOT_FOUND);
}

const FIX: &str = "l2-two-mutable-borrows-of-self";

fn fix_file(name: &str) -> String {
    let dir = content_root().join("tracks/l2-borrowing/problems/two-mutable-borrows-of-self");
    std::fs::read_to_string(dir.join(name)).unwrap()
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn fix_this_rules_block_a_passing_clone_workaround(db: PgPool) {
    let app = test_app(db);
    // Collect the names by cloning them first: compiles, passes every test, breaks two rules.
    let clone = fix_file("starter.rs").replace(
        "        for item in self.items.iter_mut().filter(|i| i.qty < 5) {\n            item.qty += 10;\n            self.record(format!(\"restocked {}\", item.name));\n        }",
        "        let low: Vec<String> = self.items.iter().filter(|i| i.qty < 5).map(|i| i.name.clone()).collect();\n        for item in self.items.iter_mut().filter(|i| i.qty < 5) {\n            item.qty += 10;\n        }\n        for name in low {\n            self.record(format!(\"restocked {name}\"));\n        }",
    );
    assert_ne!(clone, fix_file("starter.rs"), "replacement didn't apply");
    let (status, out) = call(
        &app,
        Method::POST,
        &format!("/api/problems/{FIX}/submit"),
        Some(json!({ "code": clone })),
    )
    .await;
    assert_eq!(status, StatusCode::OK, "{out}");
    assert_eq!(out["run"]["status"], "passed", "{out}");
    let rules: Vec<&str> = out["run"]["violations"]
        .as_array()
        .unwrap()
        .iter()
        .map(|v| v["rule"].as_str().unwrap())
        .collect();
    assert_eq!(rules, ["clone", "lines"]);
    assert_eq!(out["run"]["violations"][0]["line"], 13);
    assert_eq!(out["attempt"]["solved"], false);
    assert_eq!(out["solution"]["unlocked"], false);

    // The one-line fix breaks no rule and solves it.
    let (_, out) = call(
        &app,
        Method::POST,
        &format!("/api/problems/{FIX}/submit"),
        Some(json!({ "code": fix_file("solution.rs") })),
    )
    .await;
    assert_eq!(out["run"]["violations"], json!([]));
    assert_eq!(out["attempt"]["solved"], true);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn activity_picks_the_next_problem_and_counts_the_streak(db: PgPool) {
    let app = test_app(db);
    let (status, a) = call(&app, Method::GET, "/api/activity?sections=D", None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!((a["streak"].as_u64(), a["week"].as_array().map(Vec::len)), (Some(0), Some(7)));
    assert_eq!((a["next"]["reason"].as_str(), a["next"]["track_code"].as_str()), (Some("start"), Some("D9")));
    assert!(!a["next"]["excerpt"].as_str().unwrap().is_empty());

    let (_, out) = call(
        &app,
        Method::POST,
        &format!("/api/problems/{NDT}/submit"),
        Some(json!({ "code": solution() })),
    )
    .await;
    assert_eq!(out["run"]["status"], "passed");

    let (_, a) = call(&app, Method::GET, "/api/activity?sections=D", None).await;
    assert_eq!((a["streak"].as_u64(), a["week_solved"].as_u64(), a["week_unassisted"].as_u64()), (Some(1), Some(1), Some(1)));
    assert_eq!((a["recent"][0]["problem_id"].as_str(), a["recent"][0]["outcome"].as_str()), (Some(NDT), Some("solved")));
    // The solved problem's track becomes the current one; its first open problem is next.
    assert_eq!(
        (a["next"]["reason"].as_str(), a["next"]["problem_id"].as_str()),
        (Some("current"), Some(d9_ids()[0].as_str()))
    );

    // Other sections share the streak but not the recent list.
    let (_, r) = call(&app, Method::GET, "/api/activity?sections=L,S", None).await;
    assert_eq!((r["streak"].as_u64(), r["recent"].as_array().map(Vec::len)), (Some(1), Some(0)));

    let (_, tracks) = call(&app, Method::GET, "/api/tracks", None).await;
    let d9 = tracks.as_array().unwrap().iter().find(|t| t["code"] == "D9").unwrap();
    assert!(d9["readiness"].as_f64().unwrap() > 0.0);
}

/// A request with an optional cookie; returns status, the Set-Cookie value and the JSON body.
async fn raw(app: &Router, method: Method, path: &str, cookie: Option<&str>, body: Option<Value>) -> (StatusCode, Option<String>, Value) {
    let mut req = Request::builder().method(method).uri(path).header("content-type", "application/json");
    if let Some(c) = cookie {
        req = req.header("cookie", c);
    }
    let req = req.body(body.map_or_else(Body::empty, |b| Body::from(b.to_string()))).unwrap();
    let res = app.clone().oneshot(req).await.unwrap();
    let status = res.status();
    let set_cookie = res.headers().get("set-cookie").map(|v| v.to_str().unwrap().to_owned());
    let bytes = res.into_body().collect().await.unwrap().to_bytes();
    let json = if bytes.is_empty() { Value::Null } else { serde_json::from_slice(&bytes).unwrap() };
    (status, set_cookie, json)
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn passphrase_login_gates_the_api(db: PgPool) {
    use argon2::password_hash::{PasswordHasher, SaltString, rand_core::OsRng};
    let salt = SaltString::generate(&mut OsRng);
    let hash = argon2::Argon2::default().hash_password(b"open sesame", &salt).unwrap().to_string();
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../content");
    let app = test_app_auth(db, &root, AuthConfig::new(&hash, false).unwrap());

    assert_eq!(raw(&app, Method::GET, "/api/health", None, None).await.0, StatusCode::OK);
    let (status, _, body) = raw(&app, Method::GET, "/api/tracks", None, None).await;
    assert_eq!((status, body["error"].as_str()), (StatusCode::UNAUTHORIZED, Some("unauthorized")));
    let (_, _, s) = raw(&app, Method::GET, "/api/auth/session", None, None).await;
    assert_eq!(s, json!({ "required": true, "authenticated": false }));

    let (status, cookie, body) = raw(&app, Method::POST, "/api/auth/login", None, Some(json!({ "passphrase": "nope" }))).await;
    assert_eq!((status, cookie, body["error"].as_str()), (StatusCode::UNAUTHORIZED, None, Some("wrong_passphrase")));

    let (status, cookie, _) = raw(&app, Method::POST, "/api/auth/login", None, Some(json!({ "passphrase": "open sesame" }))).await;
    assert_eq!(status, StatusCode::NO_CONTENT);
    let cookie = cookie.unwrap();
    assert!(cookie.contains("HttpOnly") && cookie.contains("SameSite=Strict"), "{cookie}");
    let pair = cookie.split(';').next().unwrap().to_owned();

    assert_eq!(raw(&app, Method::GET, "/api/tracks", Some(&pair), None).await.0, StatusCode::OK);
    let (_, _, s) = raw(&app, Method::GET, "/api/auth/session", Some(&pair), None).await;
    assert_eq!(s["authenticated"], true);
    assert_eq!(raw(&app, Method::GET, "/api/tracks", Some("anneal_session=forged"), None).await.0, StatusCode::UNAUTHORIZED);

    let (status, cleared, _) = raw(&app, Method::POST, "/api/auth/logout", Some(&pair), None).await;
    assert_eq!(status, StatusCode::NO_CONTENT);
    assert!(cleared.unwrap().contains("Max-Age=0"));
    assert_eq!(raw(&app, Method::GET, "/api/tracks", Some(&pair), None).await.0, StatusCode::UNAUTHORIZED);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn editor_settings_round_trip_and_validate(db: PgPool) {
    let app = test_app(db);
    let (status, s) = call(&app, Method::GET, "/api/settings", None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(
        s["editor"],
        json!({ "font_size": 13, "font_family": "JetBrains Mono", "vim": false, "autocomplete": true, "rust_analyzer": true, "borrow_lanes": false, "live_clippy": true, "format_on_pause": false })
    );
    assert!(s["font_families"].as_array().unwrap().contains(&json!("Fira Code")));

    let e = json!({ "font_size": 16, "font_family": "Fira Code", "vim": true, "autocomplete": false, "rust_analyzer": false, "borrow_lanes": true, "live_clippy": false, "format_on_pause": true });
    assert_eq!(call(&app, Method::PUT, "/api/settings/editor", Some(e.clone())).await.0, StatusCode::OK);
    assert_eq!(call(&app, Method::GET, "/api/settings", None).await.1["editor"], e);

    // Settings saved before the workspace toggles existed read back with their defaults.
    let old = json!({ "font_size": 14, "font_family": "Fira Code", "vim": false });
    assert_eq!(call(&app, Method::PUT, "/api/settings/editor", Some(old)).await.0, StatusCode::OK);
    let editor = call(&app, Method::GET, "/api/settings", None).await.1["editor"].clone();
    assert_eq!((&editor["autocomplete"], &editor["rust_analyzer"], &editor["borrow_lanes"]), (&json!(true), &json!(true), &json!(false)));

    let too_big = json!({ "font_size": 40, "font_family": "Fira Code" });
    assert_eq!(call(&app, Method::PUT, "/api/settings/editor", Some(too_big)).await.0, StatusCode::BAD_REQUEST);
    let unknown = json!({ "font_size": 14, "font_family": "Comic Mono" });
    assert_eq!(call(&app, Method::PUT, "/api/settings/editor", Some(unknown)).await.0, StatusCode::BAD_REQUEST);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn appearance_accent_round_trips_and_validates(db: PgPool) {
    let app = test_app(db);
    let s = call(&app, Method::GET, "/api/settings", None).await.1;
    assert_eq!(s["appearance"], json!({ "accent": "copper" }));
    assert!(s["accents"].as_array().unwrap().contains(&json!("sky")));

    let a = json!({ "accent": "sky" });
    assert_eq!(call(&app, Method::PUT, "/api/settings/appearance", Some(a.clone())).await.0, StatusCode::OK);
    let s = call(&app, Method::GET, "/api/settings", None).await.1;
    assert_eq!(s["appearance"], a);
    // Saving one group leaves the other alone.
    assert_eq!(s["editor"]["font_size"], 13);

    let unknown = json!({ "accent": "chartreuse" });
    assert_eq!(call(&app, Method::PUT, "/api/settings/appearance", Some(unknown)).await.0, StatusCode::BAD_REQUEST);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn solving_schedules_reviews_and_feeds_the_dashboards(db: PgPool) {
    let app = test_app(db.clone());
    let submit = |app: &Router| {
        let app = app.clone();
        async move { call(&app, Method::POST, &format!("/api/problems/{NDT}/submit"), Some(json!({ "code": solution() }))).await }
    };

    // First, unassisted solve: graded "good", with its first review held on the consolidation day (a Sunday).
    call(&app, Method::POST, &format!("/api/problems/{NDT}/focus"), Some(json!({ "seconds": 90 }))).await;
    let (_, out) = submit(&app).await;
    assert_eq!(out["run"]["status"], "passed");
    let (status, r) = call(&app, Method::GET, "/api/reviews", None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!((r["due_today"].as_u64(), r["in_rotation"].as_u64()), (Some(0), Some(1)));
    let (grade, reps, stability, due): (String, i32, f32, chrono::DateTime<chrono::Utc>) =
        sqlx::query_as("SELECT last_grade, reps, stability, due_at FROM reviews WHERE problem_id = $1").bind(NDT).fetch_one(&db).await.unwrap();
    assert_eq!((grade.as_str(), reps), ("good", 1));
    assert!(stability > 1.0 && stability < 10.0, "a first good solve is remembered for days, not weeks: {stability}");
    assert_eq!(due.with_timezone(&chrono::Local).format("%a").to_string(), "Sun");
    assert!(due > chrono::Utc::now(), "the first review is in the future");
    let (_, stats) = call(&app, Method::GET, "/api/stats", None).await;
    assert_eq!((stats["first_run_pass"].as_f64(), stats["runs_per_solve"].as_f64()), (Some(100.0), Some(1.0)));

    // A re-solve starts a fresh attempt: hints locked, editor back to the starter.
    let (status, p) = call(&app, Method::POST, &format!("/api/problems/{NDT}/resolve"), None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!((p["attempt"]["resolve"].as_bool(), p["attempt"]["solved"].as_bool(), p["draft"].is_null()), (Some(true), Some(false), true));
    // The earlier solve still counts while the re-solve is open.
    let (_, tracks) = call(&app, Method::GET, "/api/tracks", None).await;
    let d9 = tracks.as_array().unwrap().iter().find(|t| t["code"] == "D9").unwrap();
    assert_eq!(d9["solved"], 1);

    // A re-solve that needed a hint is graded "hard": the problem is scheduled again, with less gained than a clean one.
    call(&app, Method::POST, &format!("/api/problems/{NDT}/hints"), None).await;
    submit(&app).await;
    let (grade, reps, history): (String, i32, serde_json::Value) =
        sqlx::query_as("SELECT last_grade, reps, to_jsonb(history) FROM reviews WHERE problem_id = $1").bind(NDT).fetch_one(&db).await.unwrap();
    assert_eq!((grade.as_str(), reps, history.as_array().unwrap().len()), ("hard", 2, 2));
    assert_eq!(history[1]["grade"], "hard");
    assert!(history[1]["recall_before"].as_f64().unwrap() > 0.5, "the history keeps the recall estimate at the time");
    let (_, r) = call(&app, Method::GET, "/api/reviews", None).await;
    assert_eq!(r["retention_30d"].as_f64(), Some(0.0));
    let (_, o) = call(&app, Method::GET, "/api/progress", None).await;
    assert_eq!((o["streak"].as_u64(), o["solved_year"].as_u64()), (Some(1), Some(2)));
    assert_eq!(o["heat"].as_array().unwrap().last().unwrap(), 2);
    assert_eq!(o["this_week"].as_array().unwrap().iter().map(|d| d["focus_seconds"].as_i64().unwrap()).sum::<i64>(), 90);
    assert_eq!(o["weekly"].as_array().unwrap().last().unwrap()["medium"], 2);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn run_builds_and_runs_the_scratch_main(db: PgPool) {
    let app = test_app(db);
    let (_, p) = call(&app, Method::GET, &format!("/api/problems/{NDT}"), None).await;
    assert!(p["scratch"].as_str().unwrap().contains("use solution::*;"));

    let main = "use solution::*;\nfn main() { println!(\"{:?}\", network_delay(&[(1, 2, 5)], 2, 1)); }\n";
    let (status, out) = call(&app, Method::POST, &format!("/api/problems/{NDT}/scratch/run"), Some(json!({ "lib": solution(), "main": main }))).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!((out["status"].as_str(), out["stdout"].as_str()), (Some("ok"), Some("Some(5)\n")), "{out}");

    // Both buffers were saved; Run isn't recorded as a test run.
    let (_, p) = call(&app, Method::GET, &format!("/api/problems/{NDT}"), None).await;
    assert_eq!((p["scratch"].as_str(), p["runs"].as_array().map(Vec::len)), (Some(main), Some(0)));
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn built_app_is_served_with_cache_headers(db: PgPool) {
    let dist = tempfile::tempdir().unwrap();
    std::fs::create_dir(dist.path().join("assets")).unwrap();
    std::fs::write(dist.path().join("index.html"), "<!doctype html>").unwrap();
    std::fs::write(dist.path().join("assets/index-abc123.js"), "console.log(1)").unwrap();
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let app = test_app_full(db, &root.join("content"), AuthConfig::disabled(), Some(dist.path()));
    let get = |path: &str| {
        let app = app.clone();
        let req = Request::builder().uri(path).body(Body::empty()).unwrap();
        async move { app.oneshot(req).await.unwrap() }
    };
    let cache = |res: &axum::response::Response| res.headers().get("cache-control").map(|v| v.to_str().unwrap().to_owned());

    // Hashed assets never change.
    let asset = get("/assets/index-abc123.js").await;
    assert_eq!(asset.status(), StatusCode::OK);
    assert_eq!(cache(&asset).as_deref(), Some("public, max-age=31536000, immutable"));
    // A missing asset is a real 404, uncached, not the SPA's index.html.
    let missing = get("/assets/index-gone.js").await;
    assert_eq!(missing.status(), StatusCode::NOT_FOUND);
    assert_eq!(cache(&missing), None);
    // Pages (client-side routes) get index.html and must be revalidated.
    for path in ["/", "/rust", "/p/d1-running-sum"] {
        let page = get(path).await;
        assert_eq!(page.status(), StatusCode::OK, "{path}");
        assert_eq!(cache(&page).as_deref(), Some("no-cache"), "{path}");
    }
    // The API is untouched.
    let api = get("/api/health").await;
    assert_eq!(api.status(), StatusCode::OK);
    assert_eq!(cache(&api), None);
}

/// A one-track catalog whose only problem, d99-new-name, used to be d99-old-name.
fn renamed_catalog() -> (tempfile::TempDir, anneal_content::Catalog) {
    let dir = tempfile::tempdir().unwrap();
    let track = dir.path().join("tracks/d99-fixture");
    std::fs::create_dir_all(track.join("problems/new-name")).unwrap();
    std::fs::write(
        track.join("track.toml"),
        "code = \"D99\"\nname = \"Fixture\"\nsection = \"D\"\ntier = \"core\"\norder = 99\nsummary = \"x\"\n\n[[stages]]\nslug = \"s\"\nname = \"S\"\nband = \"easy\"\n",
    )
    .unwrap();
    std::fs::write(
        track.join("problems/new-name/problem.toml"),
        "slug = \"new-name\"\ntitle = \"Renamed\"\nmode = \"write\"\nlevel = \"easy\"\nstage = \"s\"\norder = 1\nstatus = \"draft\"\ntags = []\nrenamed_from = [\"d99-old-name\"]\n",
    )
    .unwrap();
    let loaded = Catalog::load(dir.path()).unwrap();
    assert!(loaded.issues.is_empty(), "{:?}", loaded.issues);
    (dir, loaded.catalog)
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn renaming_a_problem_keeps_its_progress(db: PgPool) {
    let (_dir, catalog) = renamed_catalog();
    // Progress under the old id: a solved attempt with a run, a draft, a review, focus time and scratch.
    let attempt: i64 = sqlx::query_scalar(
        "INSERT INTO attempts (problem_id, solved_at) VALUES ('d99-old-name', now()) RETURNING id",
    )
    .fetch_one(&db)
    .await
    .unwrap();
    sqlx::query("INSERT INTO runs (attempt_id, problem_id, kind, code, status, passed, total, result) VALUES ($1, 'd99-old-name', 'submit', 'x', 'passed', 1, 1, '{}')")
        .bind(attempt)
        .execute(&db)
        .await
        .unwrap();
    sqlx::query("INSERT INTO drafts (problem_id, code) VALUES ('d99-old-name', 'old draft')").execute(&db).await.unwrap();
    sqlx::query("INSERT INTO reviews (problem_id, step, due_at, last_result, stability, difficulty, last_review, last_grade) VALUES ('d99-old-name', 2, now(), 'unassisted', 20, 5, now(), 'good')").execute(&db).await.unwrap();
    sqlx::query("INSERT INTO scratch (problem_id, code) VALUES ('d99-old-name', 'fn main() {}')").execute(&db).await.unwrap();
    // Focus time on the same day under both ids is added up.
    sqlx::query("INSERT INTO focus_time (day, problem_id, seconds) VALUES (current_date, 'd99-old-name', 60), (current_date, 'd99-new-name', 30)")
        .execute(&db)
        .await
        .unwrap();

    // Before the move, preflight knows the old id through renamed_from, so the deploy may go ahead.
    let report = anneal_api::preflight::check(&db, &catalog, &anneal_api::MIGRATOR).await.unwrap();
    assert!(report.is_ok(), "{report:?}");

    anneal_api::preflight::apply_renames(&db, &catalog).await.unwrap();
    let count = |table: &'static str, id: &'static str| {
        let db = db.clone();
        async move {
            sqlx::query_scalar::<_, i64>(&format!("SELECT count(*) FROM {table} WHERE problem_id = $1"))
                .bind(id)
                .fetch_one(&db)
                .await
                .unwrap()
        }
    };
    for table in ["attempts", "runs", "drafts", "reviews", "scratch", "focus_time"] {
        assert_eq!(count(table, "d99-old-name").await, 0, "{table} still has the old id");
        assert_eq!(count(table, "d99-new-name").await, 1, "{table} lost the row");
    }
    let seconds: i32 = sqlx::query_scalar("SELECT seconds FROM focus_time WHERE problem_id = 'd99-new-name'")
        .fetch_one(&db)
        .await
        .unwrap();
    assert_eq!(seconds, 90);
    // Running it again changes nothing.
    assert_eq!(anneal_api::preflight::apply_renames(&db, &catalog).await.unwrap(), 0);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn preflight_refuses_to_strand_progress(db: PgPool) {
    let (_dir, catalog) = renamed_catalog();
    sqlx::query("INSERT INTO attempts (problem_id) VALUES ('d99-deleted-without-a-trace')").execute(&db).await.unwrap();
    let report = anneal_api::preflight::check(&db, &catalog, &anneal_api::MIGRATOR).await.unwrap();
    assert_eq!(report.stranded, vec![("d99-deleted-without-a-trace".to_owned(), 1)]);
    assert!(report.migrations.is_empty());

    // An applied migration whose file changed is caught too.
    sqlx::query("UPDATE _sqlx_migrations SET checksum = '\\x00' WHERE version = 1").execute(&db).await.unwrap();
    let report = anneal_api::preflight::check(&db, &catalog, &anneal_api::MIGRATOR).await.unwrap();
    assert_eq!(report.migrations.len(), 1, "{:?}", report.migrations);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn format_runs_rustfmt_and_reports_parse_errors(db: PgPool) {
    let app = test_app(db);
    let (status, body) = call(&app, Method::POST, "/api/format", Some(json!({ "code": "pub fn  add(a:i32,b:i32)->i32{a+b}" }))).await;
    assert_eq!(status, StatusCode::OK, "{body}");
    assert_eq!(body["code"], "pub fn add(a: i32, b: i32) -> i32 {\n    a + b\n}\n");
    let (status, body) = call(&app, Method::POST, "/api/format", Some(json!({ "code": "pub fn broken( {" }))).await;
    assert_eq!(status, StatusCode::BAD_REQUEST);
    assert!(body["message"].as_str().unwrap().starts_with("error"), "{body}");
}

#[test]
fn editor_settings_default_to_live_clippy_without_format_on_pause() {
    // Settings saved before these fields existed still load, with live clippy on.
    let old: anneal_api::settings::EditorSettings =
        serde_json::from_value(json!({ "font_size": 14, "font_family": "Fira Code", "vim": true })).unwrap();
    assert!(old.live_clippy);
    assert!(!old.format_on_pause);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn review_settings_default_to_the_routine_and_validate(db: PgPool) {
    let app = test_app(db);
    let s = call(&app, Method::GET, "/api/settings", None).await.1;
    assert_eq!(s["srs"]["retention"], 0.85);
    assert_eq!(s["srs"]["consolidate_on"], "sun");
    assert_eq!((s["srs"]["capacity"]["mon"].as_u64(), s["srs"]["capacity"]["sat"].as_u64(), s["srs"]["capacity"]["sun"].as_u64()), (Some(1), Some(3), Some(12)));

    let mut v = s["srs"].clone();
    v["capacity"]["sun"] = json!(8);
    v["retention"] = json!(0.8);
    assert_eq!(call(&app, Method::PUT, "/api/settings/srs", Some(v)).await.0, StatusCode::OK);
    let s = call(&app, Method::GET, "/api/settings", None).await.1;
    assert_eq!((s["srs"]["capacity"]["sun"].as_u64(), s["srs"]["retention"].as_f64()), (Some(8), Some(0.8)));

    for bad in [json!({ "retention": 0.4 }), json!({ "consolidate_on": "funday" }), json!({ "capacity": { "mon": 0, "tue": 0, "wed": 0, "thu": 0, "fri": 0, "sat": 0, "sun": 0 }, "consolidate_on": null })] {
        assert_eq!(call(&app, Method::PUT, "/api/settings/srs", Some(bad)).await.0, StatusCode::BAD_REQUEST);
    }
}

/// A content root with only the DSA fixture (and optionally a retired list), so its tracks are D1 and D2.
fn dsa_root(retired: Option<&str>) -> tempfile::TempDir {
    let dir = tempfile::tempdir().unwrap();
    std::fs::create_dir_all(dir.path().join("tracks")).unwrap();
    copy_dir(&fixtures().join("dsa-root/dsa"), &dir.path().join("dsa"));
    if let Some(retired) = retired {
        std::fs::write(dir.path().join("retired.txt"), retired).unwrap();
    }
    dir
}

fn problem_of<'a>(overview: &'a Value, id: &str) -> &'a Value {
    overview["problems"].as_array().unwrap().iter().find(|p| p["id"] == id).unwrap_or_else(|| panic!("{id} missing"))
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn dsa_overview_lists_the_lists_with_their_techniques(db: PgPool) {
    let root = dsa_root(None);
    let app = test_app_with(db, root.path());
    let (status, o) = call(&app, Method::GET, "/api/dsa", None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(o["patterns"].as_array().unwrap().iter().map(|p| (p["code"].as_str().unwrap(), p["total"].as_u64().unwrap())).collect::<Vec<_>>(), [("D1", 3), ("D2", 3)]);
    assert_eq!(o["problems"].as_array().unwrap().len(), 6);
    assert_eq!(o["techniques"].as_array().unwrap().len(), 4);
    let two_sum_ii = problem_of(&o, "lc-two-sum-ii-input-array-is-sorted");
    assert_eq!((two_sum_ii["role"].as_str(), two_sum_ii["practice_of"].as_str(), two_sum_ii["pattern"].as_str()), (Some("practice"), Some("lc-valid-palindrome"), Some("D2")));
    assert_eq!(problem_of(&o, "lc-encode-and-decode-strings")["premium"], true);
    assert_eq!(problem_of(&o, "lc-contains-duplicate")["companies"][0]["name"], "Amazon");
    // Nothing logged yet.
    assert_eq!((problem_of(&o, "lc-two-sum")["state"]["solved"].clone(), problem_of(&o, "lc-two-sum")["state"]["last_grade"].clone()), (json!(false), Value::Null));
    // The goal is the NeetCode 150 without its Premium problems: 4 of the 5 in the fixture's 150.
    assert_eq!((o["plan"]["goal_total"].as_u64(), o["plan"]["goal_done"].as_u64()), (Some(4), Some(0)));
    assert_eq!(o["plan"]["next_up"][0], "lc-contains-duplicate");
    assert_eq!(o["settings"]["new_days"], json!(["mon", "tue", "wed", "thu", "fri", "sat"]));
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn logging_a_dsa_problem_feeds_progress_reviews_and_next_up(db: PgPool) {
    let root = dsa_root(None);
    let app = test_app_with(db.clone(), root.path());

    let (status, out) = call(&app, Method::POST, "/api/dsa/problems/lc-two-sum/log", Some(json!({ "grade": "good" }))).await;
    assert_eq!(status, StatusCode::OK, "{out}");
    assert!(out["due"].is_string());
    let (_, o) = call(&app, Method::GET, "/api/dsa", None).await;
    let two_sum = problem_of(&o, "lc-two-sum");
    assert_eq!((two_sum["state"]["solved"].clone(), two_sum["state"]["assisted"].clone(), two_sum["state"]["last_grade"].clone(), two_sum["state"]["reps"].clone()), (json!(true), json!(false), json!("good"), json!(1)));
    assert!(two_sum["state"]["due"].is_string());
    assert_eq!((o["plan"]["goal_done"].as_u64(), o["patterns"][0]["solved"].as_u64()), (Some(1), Some(1)));
    // The next problem follows the one just logged, skipping the Premium one outside the goal and the done one.
    assert_eq!(o["plan"]["start"], "lc-two-sum");
    assert_eq!(o["plan"]["next_up"], json!(["lc-valid-palindrome", "lc-two-sum-ii-input-array-is-sorted", "lc-contains-duplicate"]));

    // A solve through the log counts toward the streak and the Progress pages like any other.
    let (_, a) = call(&app, Method::GET, "/api/activity?sections=D", None).await;
    assert_eq!((a["streak"].as_u64(), a["week_solved"].as_u64(), a["recent"][0]["problem_id"].as_str()), (Some(1), Some(1), Some("lc-two-sum")));
    let (_, r) = call(&app, Method::GET, "/api/reviews", None).await;
    assert_eq!(r["in_rotation"], 1);

    // Needing help is "hard"; failing is "again" and doesn't count as solved.
    call(&app, Method::POST, "/api/dsa/problems/lc-valid-palindrome/log", Some(json!({ "grade": "hard" }))).await;
    call(&app, Method::POST, "/api/dsa/problems/lc-contains-duplicate/log", Some(json!({ "grade": "again" }))).await;
    let (_, o) = call(&app, Method::GET, "/api/dsa", None).await;
    assert_eq!((problem_of(&o, "lc-valid-palindrome")["state"]["solved"].clone(), problem_of(&o, "lc-valid-palindrome")["state"]["assisted"].clone()), (json!(true), json!(true)));
    let again = problem_of(&o, "lc-contains-duplicate");
    assert_eq!((again["state"]["solved"].clone(), again["state"]["last_grade"].clone(), again["state"]["lapses"].clone()), (json!(false), json!("again"), json!(1)));
    assert_eq!(o["plan"]["goal_done"], 2);

    // Logging it again is a re-solve, and it can improve the grade.
    call(&app, Method::POST, "/api/dsa/problems/lc-contains-duplicate/log", Some(json!({ "grade": "easy" }))).await;
    let kinds: Vec<String> = sqlx::query_scalar("SELECT kind FROM attempts WHERE problem_id = 'lc-contains-duplicate' ORDER BY id").fetch_all(&db).await.unwrap();
    assert_eq!(kinds, ["practice", "resolve"]);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn dsa_start_moves_where_the_next_problem_comes_from(db: PgPool) {
    let root = dsa_root(None);
    let app = test_app_with(db, root.path());
    let (status, out) = call(&app, Method::POST, "/api/dsa/start", Some(json!({ "from": "d2-two-pointers" }))).await;
    assert_eq!((status, out["start"].as_str()), (StatusCode::OK, Some("lc-valid-palindrome")));
    let (_, o) = call(&app, Method::GET, "/api/dsa", None).await;
    // From Two Pointers down, then back round to the top; the Premium problem is outside the goal.
    assert_eq!(o["plan"]["next_up"], json!(["lc-valid-palindrome", "lc-two-sum-ii-input-array-is-sorted", "lc-contains-duplicate", "lc-two-sum"]));

    let (status, _) = call(&app, Method::POST, "/api/dsa/start", Some(json!({ "from": "lc-two-sum" }))).await;
    assert_eq!(status, StatusCode::OK);
    let (_, o) = call(&app, Method::GET, "/api/dsa", None).await;
    assert_eq!(o["plan"]["next_up"][0], "lc-two-sum");
    assert_eq!(call(&app, Method::POST, "/api/dsa/start", Some(json!({ "from": "nowhere" }))).await.0, StatusCode::NOT_FOUND);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn only_dsa_problems_can_be_logged(db: PgPool) {
    let app = test_app(db);
    let (status, out) = call(&app, Method::POST, &format!("/api/dsa/problems/{NDT}/log"), Some(json!({ "grade": "good" }))).await;
    assert_eq!((status, out["error"].as_str()), (StatusCode::BAD_REQUEST, Some("bad_request")));
    assert_eq!(call(&app, Method::POST, "/api/dsa/problems/lc-nothing/log", Some(json!({ "grade": "good" }))).await.0, StatusCode::NOT_FOUND);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn the_plan_follows_the_settings(db: PgPool) {
    let root = dsa_root(None);
    let app = test_app_with(db, root.path());
    let (_, o) = call(&app, Method::GET, "/api/dsa", None).await;
    let mut settings = o["settings"].clone();
    // Solve only on Mondays and Wednesdays, two a day, with the goal widened to all lists.
    settings["new_days"] = json!(["mon", "wed"]);
    settings["new_per_day"] = json!(2);
    settings["goal"] = json!({ "list": "all", "free_only": false, "extra": 0, "custom_left": null });
    let (status, _) = call(&app, Method::PUT, "/api/settings/srs", Some(settings.clone())).await;
    assert_eq!(status, StatusCode::OK);
    let (_, o) = call(&app, Method::GET, "/api/dsa", None).await;
    assert_eq!(o["plan"]["goal_total"], 6);
    assert_eq!(o["settings"]["new_days"], json!(["mon", "wed"]));

    settings["goal"]["list"] = json!("everything");
    assert_eq!(call(&app, Method::PUT, "/api/settings/srs", Some(settings.clone())).await.0, StatusCode::BAD_REQUEST);
    settings["goal"]["list"] = json!("all");
    settings["new_days"] = json!(["mon", "mon"]);
    assert_eq!(call(&app, Method::PUT, "/api/settings/srs", Some(settings)).await.0, StatusCode::BAD_REQUEST);
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn retired_problems_lose_their_progress_without_stranding_anything(db: PgPool) {
    let root = dsa_root(Some("# removed on purpose\nd99-gone # the old one\n"));
    let loaded = Catalog::load(root.path()).unwrap();
    assert!(loaded.issues.is_empty(), "{:?}", loaded.issues);
    sqlx::query("INSERT INTO attempts (problem_id, solved_at) VALUES ('d99-gone', now()), ('lc-two-sum', now())").execute(&db).await.unwrap();
    sqlx::query("INSERT INTO focus_time (day, problem_id, seconds) VALUES (current_date, 'd99-gone', 60)").execute(&db).await.unwrap();
    // A retired id isn't "stranded": the deploy may go ahead.
    let report = anneal_api::preflight::check(&db, &loaded.catalog, &anneal_api::MIGRATOR).await.unwrap();
    assert!(report.is_ok(), "{report:?}");

    let gone = anneal_api::preflight::purge_retired(&db, &loaded.catalog).await.unwrap();
    assert_eq!(gone, 2);
    let left: Vec<String> = sqlx::query_scalar("SELECT problem_id FROM attempts").fetch_all(&db).await.unwrap();
    assert_eq!(left, ["lc-two-sum"], "only the retired problem's progress goes");
    assert_eq!(anneal_api::preflight::purge_retired(&db, &loaded.catalog).await.unwrap(), 0, "idempotent");
}

#[test]
fn a_current_problem_cannot_also_be_retired() {
    let root = dsa_root(Some("lc-two-sum\n"));
    let loaded = Catalog::load(root.path()).unwrap();
    assert!(loaded.issues.iter().any(|i| i.message.contains("lc-two-sum is retired but also a current problem")), "{:?}", loaded.issues);
}
