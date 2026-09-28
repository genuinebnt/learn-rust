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
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let loaded = Catalog::load(&root.join("content")).expect("content");
    loaded.catalog.track("D9").expect("D9").problems.iter().map(|p| p.id.clone()).collect()
}

fn test_app(db: PgPool) -> Router {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    test_app_with(db, &root.join("content"))
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
            ai: anneal_api::ai::AiSlot::new(None),
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
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../content/tracks/d9-graphs/problems/network-delay-time/solution.rs");
    std::fs::read_to_string(root).unwrap()
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
        "hard"
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
    let dir = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../content/tracks/l2-borrowing/problems/two-mutable-borrows-of-self");
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
    assert_eq!((a["next"]["reason"].as_str(), a["next"]["track_code"].as_str()), (Some("start"), Some("D1")));
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
    let app = test_app(db);
    let submit = |app: &Router| {
        let app = app.clone();
        async move { call(&app, Method::POST, &format!("/api/problems/{NDT}/submit"), Some(json!({ "code": solution() }))).await }
    };

    // First, unassisted solve: one retention check in 21 days.
    call(&app, Method::POST, &format!("/api/problems/{NDT}/focus"), Some(json!({ "seconds": 90 }))).await;
    let (_, out) = submit(&app).await;
    assert_eq!(out["run"]["status"], "passed");
    let (status, r) = call(&app, Method::GET, "/api/reviews", None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!((r["due_today"].as_u64(), r["in_rotation"].as_u64()), (Some(0), Some(1)));
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

    // An assisted re-solve resets the ladder to 3 days.
    call(&app, Method::POST, &format!("/api/problems/{NDT}/hints"), None).await;
    submit(&app).await;
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
    sqlx::query("INSERT INTO reviews (problem_id, step, due_at, last_result) VALUES ('d99-old-name', 2, now(), 'unassisted')").execute(&db).await.unwrap();
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
async fn ai_routes_explain_themselves_when_no_key_is_set(db: PgPool) {
    let app = test_app(db);
    let (status, body) = call(&app, Method::GET, "/api/ai/status", None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["enabled"], false);
    let (status, body) = call(&app, Method::POST, "/api/ai/chat/d1-running-sum", Some(json!({ "message": "hi" }))).await;
    assert_eq!(status, StatusCode::CONFLICT);
    assert_eq!(body["error"], "ai_off");
    assert!(body["message"].as_str().unwrap().contains("GEMINI_API_KEY"));
    let (status, body) = call(&app, Method::GET, "/api/ai/patterns", None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(body, Value::Null);
    // History works without a key (it's just stored messages).
    let (status, body) = call(&app, Method::GET, "/api/ai/chat/d1-running-sum", None).await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(body, json!([]));
}

#[sqlx::test(migrator = "anneal_api::MIGRATOR")]
async fn ai_key_setting_never_returns_the_key(db: PgPool) {
    let app = test_app(db.clone());
    let (status, body) = call(&app, Method::GET, "/api/ai/config", None).await;
    assert_eq!(status, StatusCode::OK);
    // The test process may have a key in its environment; either way the key itself never comes back.
    assert!(body.get("api_key").is_none());
    let (status, body) = call(&app, Method::PUT, "/api/ai/config", Some(json!({ "provider": "gemini" }))).await;
    assert_eq!(status, StatusCode::BAD_REQUEST, "{body}");
    assert!(body["message"].as_str().unwrap().contains("API key"));
    // A saved key shows only its last four characters.
    sqlx::query("INSERT INTO settings (key, value) VALUES ('ai', '{\"provider\": \"gemini\", \"api_key\": \"secret-key-9Qk\"}')")
        .execute(&db)
        .await
        .unwrap();
    let body = call(&app, Method::GET, "/api/ai/config", None).await.1;
    assert_eq!(body["source"], "settings");
    assert_eq!(body["key_hint"], "…-9Qk");
    assert!(!body.to_string().contains("secret-key"));
    let (status, body) = call(&app, Method::DELETE, "/api/ai/config", None).await;
    assert_eq!(status, StatusCode::OK, "{body}");
    assert_ne!(body["source"], "settings");
}
