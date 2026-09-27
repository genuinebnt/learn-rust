//! Each test gets its own database from `#[sqlx::test]` (needs the compose Postgres)
//! and runs code with host cargo.

use std::path::Path;
use std::sync::Arc;

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

fn test_app(db: PgPool) -> Router {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let loaded = Catalog::load(&root.join("content")).expect("content");
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
        (Some(35), Some(1), Some(0))
    );
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
        (Some(16), Some(35))
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
        (Some(4), Some(6))
    );
    let hidden = out["run"]["tests"]
        .as_array()
        .unwrap()
        .iter()
        .find(|t| t["suite"] == "hidden")
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
    let app = test_app(db);
    let (status, body) = call(
        &app,
        Method::POST,
        "/api/problems/d9-word-ladder/run",
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
