//! Python practice runs, end to end on the host (needs `python3`).

use std::path::Path;
use std::time::Duration;

use anneal_runner::{Outcome, PySubmission, RunStatus, Runner, RunnerConfig, Sandbox};

const TESTS: &str = r#"
from anneal_prelude import check, ensure
from solution import double, order


def test_double():
    check("double(2)", double(2), 4)


def test_wrong_value():
    check("double(3)", double(3), 6)


def test_prints_and_passes():
    print("hello from the test")
    assert double(0) == 0


def test_property():
    got = order([3, 1, 2])
    ensure(sorted(got) == [1, 2, 3], "must contain every item once")
"#;

fn runner() -> Runner {
    let mut cfg = RunnerConfig::new(Sandbox::Host, Path::new(env!("CARGO_TARGET_TMPDIR")).join("anneal-py"));
    cfg.test_timeout = Duration::from_secs(30);
    Runner::new(cfg)
}

async fn run(code: &str, hidden: Option<&str>) -> anneal_runner::RunResult {
    runner().run_python(&PySubmission { code, visible_tests: TESTS, hidden_tests: hidden }).await.expect("runner")
}

#[tokio::test]
async fn passes_fails_and_reports_checks() {
    let good = "def double(x):\n    return x * 2\n\n\ndef order(xs):\n    return sorted(xs)\n";
    let r = run(good, None).await;
    assert_eq!((r.status, r.passed, r.total), (RunStatus::Passed, 4, 4), "{:?}", r.tests);
    let printed = r.tests.iter().find(|t| t.name == "prints_and_passes").unwrap();
    assert_eq!(printed.stdout.trim(), "hello from the test");

    let wrong = "def double(x):\n    return x + x if x < 3 else 0\n\n\ndef order(xs):\n    return xs[:2]\n";
    let r = run(wrong, None).await;
    assert_eq!(r.status, RunStatus::Failed);
    let t = r.tests.iter().find(|t| t.name == "wrong_value").unwrap();
    assert_eq!(t.outcome, Outcome::Failed);
    let c = t.check.as_ref().expect("a check mismatch");
    assert_eq!((c.input.as_str(), c.expected.as_str(), c.got.as_str()), ("double(3)", "6", "0"));
    let prop = r.tests.iter().find(|t| t.name == "property").unwrap();
    assert!(prop.panic.as_deref().unwrap().contains("must contain every item once"), "{prop:?}");
}

#[tokio::test]
async fn syntax_and_indentation_errors_point_at_the_line() {
    let r = run("def double(x):\nreturn x\n", None).await;
    assert_eq!(r.status, RunStatus::CompileError);
    let d = &r.diagnostics[0];
    assert!(d.message.to_lowercase().contains("indent"), "{}", d.message);
    assert_eq!((d.spans[0].file.as_str(), d.spans[0].line_start), ("solution.py", 2));

    let r = run("def double(x):\n    return x\n  y = 1\n", None).await;
    assert_eq!(r.status, RunStatus::CompileError);
    assert_eq!(r.diagnostics[0].spans[0].line_start, 3);
}

#[tokio::test]
async fn runtime_errors_timeouts_and_import_errors() {
    let boom = "def double(x):\n    return 1 // 0\n\n\ndef order(xs):\n    return xs\n";
    let r = run(boom, None).await;
    let t = r.tests.iter().find(|t| t.name == "double").unwrap();
    assert!(t.panic.as_deref().unwrap().contains("ZeroDivisionError") && t.panic.as_deref().unwrap().contains("solution.py line 2"), "{t:?}");

    let slow = "def double(x):\n    while True:\n        pass\n\n\ndef order(xs):\n    return xs\n";
    let r = run(slow, None).await;
    assert_eq!(r.status, RunStatus::Timeout);
    assert!(r.tests.iter().any(|t| t.outcome == Outcome::TimedOut));

    let r = run("raise RuntimeError('oops')\n", None).await;
    assert_eq!(r.status, RunStatus::CompileError);
    assert!(r.diagnostics[0].message.contains("oops"), "{}", r.diagnostics[0].message);

    let r = run("def double(x):\n    return x * 2\n", None).await; // order() is missing
    assert_eq!(r.status, RunStatus::CompileError, "{:?}", r.diagnostics);
    assert!(r.diagnostics[0].message.contains("doesn't define `order`"), "{}", r.diagnostics[0].message);
}

#[tokio::test]
async fn hidden_tests_run_only_on_submit() {
    let good = "def double(x):\n    return x * 2\n\n\ndef order(xs):\n    return sorted(xs)\n";
    let hidden = "from anneal_prelude import check\nfrom solution import double\n\n\ndef test_big():\n    check('double(10**6)', double(10**6), 2 * 10**6)\n";
    let run_only = run(good, None).await;
    assert_eq!(run_only.total, 4);
    let submit = run(good, Some(hidden)).await;
    assert_eq!((submit.total, submit.status), (5, RunStatus::Passed));
    assert!(submit.tests.iter().any(|t| t.suite == anneal_runner::Suite::Hidden));
}
