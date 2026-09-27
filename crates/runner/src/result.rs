use serde::{Deserialize, Serialize};

/// Everything one Run or Submit produced.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunResult {
    pub status: RunStatus,
    /// Compiler errors and warnings plus clippy lints, for user files only.
    pub diagnostics: Vec<Diagnostic>,
    pub tests: Vec<TestOutcome>,
    pub passed: usize,
    pub total: usize,
    pub duration_ms: u64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum RunStatus {
    /// Every test passed.
    Passed,
    /// It compiled, and at least one test failed.
    Failed,
    CompileError,
    /// Compilation or the tests ran past their time limit.
    Timeout,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Diagnostic {
    pub level: Level,
    /// `E0499`, or a lint name like `clippy::needless_range_loop`.
    pub code: Option<String>,
    pub message: String,
    /// rustc's own rendering, as it would print in a terminal.
    pub rendered: String,
    pub spans: Vec<Span>,
    /// `help:` and `note:` lines attached to the diagnostic.
    pub notes: Vec<String>,
}

impl Diagnostic {
    pub fn is_error(&self) -> bool {
        self.level == Level::Error
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Level {
    Error,
    Warning,
    Note,
    Help,
}

/// A labelled source range. Borrow lanes are drawn from these.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Span {
    /// Relative to the workspace, e.g. `src/lib.rs`.
    pub file: String,
    pub line_start: u32,
    pub line_end: u32,
    pub col_start: u32,
    pub col_end: u32,
    pub primary: bool,
    pub label: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestOutcome {
    pub suite: Suite,
    pub name: String,
    pub outcome: Outcome,
    pub duration_ms: Option<f64>,
    /// Set when the test used `check!` and the values differed.
    pub check: Option<Check>,
    /// The panic message, without the location line.
    pub panic: Option<String>,
    /// What the test printed, minus anneal's own `check!` report.
    pub stdout: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Suite {
    Visible,
    Hidden,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Outcome {
    Passed,
    Failed,
    Ignored,
    /// Started but didn't finish before the time limit.
    TimedOut,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Check {
    pub input: String,
    pub expected: String,
    pub got: String,
}
