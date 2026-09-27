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
        None,
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
        json!({ "font_size": 13, "font_family": "JetBrains Mono", "vim": false, "autocomplete": true, "rust_analyzer": true, "borrow_lanes": false })
    );
    assert!(s["font_families"].as_array().unwrap().contains(&json!("Fira Code")));

    let e = json!({ "font_size": 16, "font_family": "Fira Code", "vim": true, "autocomplete": false, "rust_analyzer": false, "borrow_lanes": true });
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
