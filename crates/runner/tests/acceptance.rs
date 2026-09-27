//! End-to-end runs against real problems in `content/`.
//!
//! Host tests run with plain `cargo test`. The Docker test needs the sandbox image
//! (`docker build -t anneal-runner:1.98 -f docker/runner.Dockerfile docker`) and runs
//! with `cargo test -p anneal-runner -- --ignored`.

use std::path::{Path, PathBuf};
use std::time::Duration;

use anneal_content::{Catalog, Problem};
use anneal_runner::{
    Outcome, RunResult, RunStatus, Runner, RunnerConfig, Sandbox, Submission, Suite,
};

/// The workspace from the WorkspaceSplit design: the `u32::MAX` sentinel leaks out.
const NETWORK_DELAY_SENTINEL_BUG: &str = r#"use std::cmp::Reverse;
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

fn content_root() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../content")
}

fn problem(catalog: &Catalog, id: &str) -> (String, String, String, String) {
    let (_, p): (_, &Problem) = catalog
        .problem(id)
        .unwrap_or_else(|| panic!("no problem {id}"));
    let f = &p.files;
    (
        f.starter.clone().expect("starter"),
        f.solution.clone().expect("solution"),
        f.visible_tests.clone().expect("visible tests"),
        f.hidden_tests.clone().expect("hidden tests"),
    )
}

fn runner(sandbox: Sandbox) -> Runner {
    let mut cfg = RunnerConfig::new(
        sandbox,
        Path::new(env!("CARGO_TARGET_TMPDIR")).join("anneal"),
    );
    cfg.test_timeout = Duration::from_secs(20);
    Runner::new(cfg)
}

fn catalog() -> Catalog {
    let loaded = Catalog::load(&content_root()).expect("content loads");
    assert!(
        loaded.issues.is_empty(),
        "content issues: {:?}",
        loaded.issues
    );
    loaded.catalog
}

async fn submit(r: &Runner, id: &str, lib_rs: &str, visible: &str, hidden: &str) -> RunResult {
    r.run(
        id,
        &Submission {
            lib_rs,
            visible_tests: visible,
            hidden_tests: Some(hidden),
        },
    )
    .await
    .expect("runner")
}

fn failing(r: &RunResult) -> Vec<(Suite, &str)> {
    r.tests
        .iter()
        .filter(|t| t.outcome != Outcome::Passed)
        .map(|t| (t.suite, t.name.as_str()))
        .collect()
}

#[tokio::test]
async fn network_delay_sentinel_bug_scores_4_of_6() {
    let c = catalog();
    let (_, _, visible, hidden) = problem(&c, "d9-network-delay-time");
    let r = submit(
        &runner(Sandbox::Host),
        "d9-network-delay-time",
        NETWORK_DELAY_SENTINEL_BUG,
        &visible,
        &hidden,
    )
    .await;

    assert_eq!(r.status, RunStatus::Failed);
    assert_eq!((r.passed, r.total), (4, 6));
    assert_eq!(
        failing(&r),
        vec![
            (Suite::Hidden, "dense_n100"),
            (Suite::Visible, "unreachable_returns_none")
        ]
    );
    let unreachable = r
        .tests
        .iter()
        .find(|t| t.name == "unreachable_returns_none")
        .unwrap();
    let check = unreachable.check.as_ref().expect("check! report");
    assert_eq!(
        (check.expected.as_str(), check.got.as_str()),
        ("None", "Some(4294967295)")
    );
    assert_eq!(check.input, "times = [(1,2,1)], n = 3, k = 1");
}

#[tokio::test]
async fn network_delay_reference_passes_6_of_6() {
    let c = catalog();
    let (_, solution, visible, hidden) = problem(&c, "d9-network-delay-time");
    let r = submit(
        &runner(Sandbox::Host),
        "d9-network-delay-time",
        &solution,
        &visible,
        &hidden,
    )
    .await;
    assert_eq!(r.status, RunStatus::Passed, "{r:#?}");
    assert_eq!((r.passed, r.total), (6, 6));
}

#[tokio::test]
async fn run_without_hidden_tests_reports_visible_only() {
    let c = catalog();
    let (_, _, visible, _) = problem(&c, "d9-network-delay-time");
    let sub = Submission {
        lib_rs: NETWORK_DELAY_SENTINEL_BUG,
        visible_tests: &visible,
        hidden_tests: None,
    };
    let r = runner(Sandbox::Host)
        .run("d9-network-delay-time", &sub)
        .await
        .unwrap();
    assert_eq!((r.passed, r.total), (4, 5));
    assert!(r.tests.iter().all(|t| t.suite == Suite::Visible));
}

#[tokio::test]
async fn fix_this_starter_reports_e0499_with_both_borrows() {
    let c = catalog();
    let (starter, _, visible, hidden) = problem(&c, "l2-two-mutable-borrows-of-self");
    let r = submit(
        &runner(Sandbox::Host),
        "l2-two-mutable-borrows-of-self",
        &starter,
        &visible,
        &hidden,
    )
    .await;

    assert_eq!(r.status, RunStatus::CompileError);
    assert!(r.tests.is_empty());
    let e = r
        .diagnostics
        .iter()
        .find(|d| d.code.as_deref() == Some("E0499"))
        .expect("E0499");
    // Borrow lanes are drawn from these: the loop's borrow on line 13, the conflict on line 15.
    let lines: Vec<(u32, bool)> = e.spans.iter().map(|s| (s.line_start, s.primary)).collect();
    assert!(lines.contains(&(15, true)), "{lines:?}");
    assert!(lines.contains(&(13, false)), "{lines:?}");
}

#[tokio::test]
async fn fix_this_solution_passes_visible_and_hidden() {
    let c = catalog();
    let (_, solution, visible, hidden) = problem(&c, "l2-two-mutable-borrows-of-self");
    let r = submit(
        &runner(Sandbox::Host),
        "l2-two-mutable-borrows-of-self",
        &solution,
        &visible,
        &hidden,
    )
    .await;
    assert_eq!(r.status, RunStatus::Passed, "{r:#?}");
    assert_eq!((r.passed, r.total), (5, 5));
}

#[tokio::test]
async fn infinite_loop_times_out_and_is_killed() {
    let c = catalog();
    let (_, _, visible, _) = problem(&c, "d9-network-delay-time");
    let spin = "pub fn network_delay(_: &[(usize, usize, u32)], _: usize, _: usize) -> Option<u32> { loop { std::hint::spin_loop() } }";
    let mut cfg = RunnerConfig::new(
        Sandbox::Host,
        Path::new(env!("CARGO_TARGET_TMPDIR")).join("anneal"),
    );
    cfg.test_timeout = Duration::from_secs(3);
    let r = Runner::new(cfg)
        .run(
            "d9-network-delay-time-spin",
            &Submission {
                lib_rs: spin,
                visible_tests: &visible,
                hidden_tests: None,
            },
        )
        .await
        .unwrap();
    assert_eq!(r.status, RunStatus::Timeout);
    assert!(
        r.tests.iter().any(|t| t.outcome == Outcome::TimedOut),
        "{r:#?}"
    );
}

#[tokio::test]
#[ignore = "needs Docker and the anneal-runner:1.98 image"]
async fn docker_sandbox_matches_host() {
    let c = catalog();
    let (_, solution, visible, hidden) = problem(&c, "d9-network-delay-time");
    let docker = runner(Sandbox::docker("anneal-runner:1.98"));
    let bug = submit(
        &docker,
        "d9-network-delay-time",
        NETWORK_DELAY_SENTINEL_BUG,
        &visible,
        &hidden,
    )
    .await;
    assert_eq!(
        (bug.status, bug.passed, bug.total),
        (RunStatus::Failed, 4, 6),
        "{bug:#?}"
    );
    let ok = submit(
        &docker,
        "d9-network-delay-time",
        &solution,
        &visible,
        &hidden,
    )
    .await;
    assert_eq!(
        (ok.status, ok.passed, ok.total),
        (RunStatus::Passed, 6, 6),
        "{ok:#?}"
    );
}
