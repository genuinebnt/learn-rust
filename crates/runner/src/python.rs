//! Runs a Python practice problem: writes the user's `solution.py`, the problem's test modules and anneal's
//! harness into a throwaway directory and runs `python3 _harness.py visible [hidden]` in the sandbox. The harness
//! prints one JSON event per line, which become the same [`RunResult`] a Rust problem produces.

use std::path::Path;
use std::time::Instant;

use serde::Deserialize;

use crate::exec::{self, Program};
use crate::result::{Check, Diagnostic, Level, Outcome, RunResult, RunStatus, Span, Suite, TestOutcome};
use crate::{Runner, RunnerError};

const HARNESS: &str = include_str!("python_harness.py");
const PRELUDE: &str = include_str!("python_prelude.py");
/// The file name diagnostics point at; the web app shows it as the editor's tab.
pub const SOLUTION_FILE: &str = "solution.py";

/// What to run: the user's code plus the problem's tests.
#[derive(Debug, Clone, Copy)]
pub struct PySubmission<'a> {
    pub code: &'a str,
    pub visible_tests: &'a str,
    /// Present on Submit, absent on Run.
    pub hidden_tests: Option<&'a str>,
}

#[derive(Debug, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
enum Event {
    Syntax { message: String, line: u32, col: u32, text: String },
    ImportError { message: String, line: u32, trace: String },
    TestFileError { message: String, trace: String },
    /// The tests import a name `solution.py` doesn't define.
    Missing { message: String },
    Test { suite: String, name: String, outcome: String, ms: f64, check: Option<PyCheck>, panic: Option<String>, stdout: String },
    Done,
}

#[derive(Debug, Deserialize)]
struct PyCheck {
    input: String,
    expected: String,
    got: String,
}

impl Runner {
    /// Runs `sub` with Python. Nothing is shared between runs, so there is no cache key.
    pub async fn run_python(&self, sub: &PySubmission<'_>) -> Result<RunResult, RunnerError> {
        let cfg = &self.config;
        let runs = cfg.work_root.join("runs");
        std::fs::create_dir_all(&runs).map_err(|e| RunnerError::io("create work root", e))?;
        let work = tempfile::Builder::new().prefix("py-").tempdir_in(&runs).map_err(|e| RunnerError::io("create run dir", e))?;
        write(work.path(), sub)?;
        // The sandbox mounts a target directory next to the work directory; Python has no use for it.
        let target = work.path().join(".target");
        std::fs::create_dir_all(&target).map_err(|e| RunnerError::io("create target dir", e))?;

        let mut args = vec!["-B", "_harness.py", "visible"];
        if sub.hidden_tests.is_some() {
            args.push("hidden");
        }
        let start = Instant::now();
        let out = exec::run(&cfg.sandbox, work.path(), &target, Program::Python, &args, cfg.test_timeout).await?;
        let (status, diagnostics, tests) = interpret(&out.stdout, &out.stderr, out.timed_out, out.exit_code, sub.code);
        let passed = tests.iter().filter(|t| t.outcome == Outcome::Passed).count();
        let total = tests.len();
        Ok(RunResult { status, diagnostics, tests, passed, total, duration_ms: start.elapsed().as_millis() as u64 })
    }
}

fn write(dir: &Path, sub: &PySubmission<'_>) -> Result<(), RunnerError> {
    let put = |name: &str, text: &str| std::fs::write(dir.join(name), text).map_err(|e| RunnerError::io("write python file", e));
    put("solution.py", sub.code)?;
    put("visible.py", sub.visible_tests)?;
    if let Some(hidden) = sub.hidden_tests {
        put("hidden.py", hidden)?;
    }
    put("anneal_prelude.py", PRELUDE)?;
    put("_harness.py", HARNESS)
}

/// Turns the harness's output into a status, diagnostics and test outcomes.
fn interpret(stdout: &str, stderr: &str, timed_out: bool, exit_code: Option<i32>, code: &str) -> (RunStatus, Vec<Diagnostic>, Vec<TestOutcome>) {
    let mut diagnostics = Vec::new();
    let mut tests = Vec::new();
    let mut finished = false;
    for line in stdout.lines() {
        let Some(json) = line.strip_prefix("@@anneal@@") else { continue };
        let Ok(event) = serde_json::from_str::<Event>(json) else { continue };
        match event {
            Event::Syntax { message, line, col, text } => {
                let rendered = format!("SyntaxError: {message}\n  {SOLUTION_FILE}, line {line}\n    {text}");
                diagnostics.push(diagnostic("SyntaxError", &message, rendered, line, col, code));
                return (RunStatus::CompileError, diagnostics, Vec::new());
            }
            Event::ImportError { message, line, trace } => {
                let rendered = format!("{message}\n{trace}");
                diagnostics.push(diagnostic("ImportError", &format!("{SOLUTION_FILE} fails when it loads: {message}"), rendered, line, 1, code));
                return (RunStatus::CompileError, diagnostics, Vec::new());
            }
            Event::Missing { message } => {
                // "cannot import name 'order' from 'solution' (...)": say which name, in the user's terms.
                let name = message.split('\'').nth(1).unwrap_or("a function the tests call");
                diagnostics.push(diagnostic("MissingName", &format!("{SOLUTION_FILE} doesn't define `{name}`, which the tests call. Keep the starter's function names and signatures."), message, 1, 1, code));
                return (RunStatus::CompileError, diagnostics, Vec::new());
            }
            Event::TestFileError { message, trace } => {
                // The problem's own tests are broken: that's a content bug, shown as a plain error.
                diagnostics.push(Diagnostic {
                    level: Level::Error,
                    code: Some("TestFileError".into()),
                    message: format!("the problem's tests failed to load: {message}"),
                    rendered: trace,
                    spans: Vec::new(),
                    notes: Vec::new(),
                });
                return (RunStatus::CompileError, diagnostics, Vec::new());
            }
            Event::Test { suite, name, outcome, ms, check, panic, stdout } => tests.push(TestOutcome {
                suite: if suite == "hidden" { Suite::Hidden } else { Suite::Visible },
                name,
                outcome: match outcome.as_str() {
                    "passed" => Outcome::Passed,
                    "timed_out" => Outcome::TimedOut,
                    _ => Outcome::Failed,
                },
                duration_ms: Some(ms),
                check: check.map(|c| Check { input: c.input, expected: c.expected, got: c.got }),
                panic,
                stdout,
            }),
            Event::Done => finished = true,
        }
    }
    let status = if timed_out || tests.iter().any(|t| t.outcome == Outcome::TimedOut) {
        RunStatus::Timeout
    } else if !finished {
        // The harness died without finishing: the sandbox killed it (memory) or something outside Python broke.
        diagnostics.push(Diagnostic {
            level: Level::Error,
            code: Some("Crashed".into()),
            message: format!("the run stopped early (exit code {exit_code:?})"),
            rendered: stderr.trim().to_owned(),
            spans: Vec::new(),
            notes: Vec::new(),
        });
        RunStatus::CompileError
    } else if !tests.is_empty() && tests.iter().all(|t| t.outcome == Outcome::Passed) {
        RunStatus::Passed
    } else {
        RunStatus::Failed
    };
    (status, diagnostics, tests)
}

fn diagnostic(code_name: &str, message: &str, rendered: String, line: u32, col: u32, source: &str) -> Diagnostic {
    let line_len = source.lines().nth(line.saturating_sub(1) as usize).map_or(1, |l| l.chars().count() as u32 + 1);
    Diagnostic {
        level: Level::Error,
        code: Some(code_name.to_owned()),
        message: message.to_owned(),
        rendered,
        spans: vec![Span {
            file: SOLUTION_FILE.to_owned(),
            line_start: line,
            line_end: line,
            col_start: col.max(1),
            col_end: line_len.max(col.max(1) + 1),
            primary: true,
            label: None,
        }],
        notes: Vec::new(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn event(json: &str) -> String {
        format!("print noise\n@@anneal@@{json}\n")
    }

    #[test]
    fn a_syntax_error_becomes_a_compile_error_with_a_span() {
        let out = event(r#"{"kind":"syntax","message":"expected ':'","line":2,"col":9,"text":"def f()"}"#);
        let (status, diags, tests) = interpret(&out, "", false, Some(0), "x = 1\ndef f()\n");
        assert_eq!(status, RunStatus::CompileError);
        assert!(tests.is_empty());
        assert_eq!((diags[0].spans[0].line_start, diags[0].spans[0].col_start), (2, 9));
    }

    #[test]
    fn tests_map_to_outcomes_and_the_status_follows() {
        let mut out = String::new();
        out += &event(r#"{"kind":"test","suite":"visible","name":"a","outcome":"passed","ms":1.5,"check":null,"panic":null,"stdout":"hi"}"#);
        out += &event(r#"{"kind":"test","suite":"hidden","name":"b","outcome":"failed","ms":2.0,"check":{"input":"f(1)","expected":"2","got":"3"},"panic":"x","stdout":""}"#);
        out += &event(r#"{"kind":"done"}"#);
        let (status, _, tests) = interpret(&out, "", false, Some(0), "");
        assert_eq!(status, RunStatus::Failed);
        assert_eq!((tests[0].outcome, tests[0].stdout.as_str()), (Outcome::Passed, "hi"));
        assert_eq!((tests[1].suite, tests[1].check.as_ref().map(|c| c.got.as_str())), (Suite::Hidden, Some("3")));

        let all_pass = event(r#"{"kind":"test","suite":"visible","name":"a","outcome":"passed","ms":1.0,"check":null,"panic":null,"stdout":""}"#) + &event(r#"{"kind":"done"}"#);
        assert_eq!(interpret(&all_pass, "", false, Some(0), "").0, RunStatus::Passed);
    }

    #[test]
    fn a_missing_function_is_named() {
        let out = event(r#"{"kind":"missing","message":"cannot import name 'order' from 'solution' (/work/solution.py)","name":"order","line":1}"#);
        let (status, diags, _) = interpret(&out, "", false, Some(0), "def double(x):\n    return x\n");
        assert_eq!(status, RunStatus::CompileError);
        assert!(diags[0].message.contains("doesn't define `order`"), "{}", diags[0].message);
    }

    #[test]
    fn timeouts_and_crashes_are_reported() {
        let slow = event(r#"{"kind":"test","suite":"visible","name":"a","outcome":"timed_out","ms":4000.0,"check":null,"panic":"slow","stdout":""}"#) + &event(r#"{"kind":"done"}"#);
        assert_eq!(interpret(&slow, "", false, Some(0), "").0, RunStatus::Timeout);
        assert_eq!(interpret("", "", true, None, "").0, RunStatus::Timeout);
        let (status, diags, _) = interpret("", "Killed", false, Some(137), "");
        assert_eq!((status, diags[0].code.as_deref()), (RunStatus::CompileError, Some("Crashed")));
    }
}
