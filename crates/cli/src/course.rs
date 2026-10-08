//! `anneal course`: a CodeCrafters-style course (docs/BUSTUB.md). The learner works in a normal Cargo repo,
//! `anneal course test` runs the current stage's tests, and a git `pre-push` hook records the result.
//!
//! Authoring side: `courses/<id>/reference/` is the whole repo with the solution written out and each part
//! a learner writes marked `// @begin <stage>` ... `// @end`, with the stub in `//~` lines. `build` renders the repo as it
//! is after any stage; `verify` checks that every stage's tests fail before it and pass after it.

use std::collections::{BTreeMap, HashMap};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, ExitCode, Stdio};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use anyhow::{Context, bail};
use clap::Subcommand;

use crate::course_sync;
use crate::course_unlock;
use serde::{Deserialize, Serialize};

#[derive(Subcommand)]
pub enum CourseCmd {
    /// Create a repo for a course: copies the template, runs `git init`, installs the hooks.
    Init {
        /// Course id, e.g. bustub.
        course: String,
        /// Where to create the repo (default: the course's repo name in the current directory).
        dir: Option<PathBuf>,
        /// The directory holding the courses.
        #[arg(long, default_value = "courses")]
        courses: PathBuf,
    },
    /// Sign in to the anneal web app, so runs are reported there and its stage pages show your progress.
    Login {
        /// The app's address, e.g. https://anneal.genuinebasil.dev (or http://127.0.0.1:8787 locally).
        url: String,
    },
    /// Authoring: check the course against docs/COURSE_STANDARDS.md (learn lines, concepts, a Performance section, hints, a short Tests summary).
    Lint {
        #[arg(long, default_value = "bustub")]
        course: String,
        #[arg(long, default_value = "courses")]
        courses: PathBuf,
        /// Check every module, not only the published ones.
        #[arg(long)]
        all: bool,
    },
    /// Authoring: upload each stage's solution diff (from reference/) to the web app you signed in to.
    Solutions {
        #[arg(long, default_value = "bustub")]
        course: String,
        /// The directory holding the courses.
        #[arg(long, default_value = "courses")]
        courses: PathBuf,
        /// Write the diffs to this JSON file instead of uploading them.
        #[arg(long)]
        out: Option<PathBuf>,
        /// Only these stage ids.
        stages: Vec<String>,
    },
    /// Where you are: the current module and stage, and what's done.
    Status,
    /// Print a stage's README (default: the current stage).
    Show { stage: Option<String> },
    /// Run a stage's tests (default: the current stage, then the earlier stages as a regression check).
    Test {
        /// A stage id, e.g. 1a-03.
        stage: Option<String>,
        /// Run every passed stage's tests too (the default for the current stage) and nothing is skipped.
        #[arg(long)]
        all: bool,
    },
    /// Show the next stage's README. Run after the current stage passes.
    Next,
    /// Install (or reinstall) the git hooks in this repo.
    Hooks,
    /// Bring in the stages, tests and stubs added since `init` (new modules), without touching your code.
    Update {
        #[arg(long, default_value = "bustub")]
        course: String,
        #[arg(long, default_value = "courses")]
        courses: PathBuf,
    },
    /// What a git hook runs. `anneal course hook pre-push`.
    Hook { name: String },
    /// Authoring: render the repo as it is after a stage into a directory.
    Build {
        /// Render after this stage. Without it: the template (before stage 1).
        #[arg(long, conflicts_with = "full")]
        stage: Option<String>,
        /// Render the whole solution (all stages done).
        #[arg(long)]
        full: bool,
        /// Output directory (created; existing files are overwritten).
        out: PathBuf,
        #[arg(long, default_value = "bustub")]
        course: String,
        #[arg(long, default_value = "courses")]
        courses: PathBuf,
    },
    /// Authoring: check every stage's tests fail before the stage and pass after it.
    Verify {
        #[arg(long, default_value = "bustub")]
        course: String,
        #[arg(long, default_value = "courses")]
        courses: PathBuf,
        /// Only this stage (and the regression of the stages before it); `unlock` checks only that every module's unlock state compiles.
        #[arg(long)]
        stage: Option<String>,
        /// Start at this stage (earlier stages are assumed fine).
        #[arg(long)]
        from: Option<String>,
        /// Scratch directory for the rendered repo. Reused between runs so cargo's cache stays warm.
        #[arg(long)]
        work: Option<PathBuf>,
    },
    /// Authoring: regenerate courses/<id>/template from the reference (the repo learners start from).
    Template {
        #[arg(long, default_value = "bustub")]
        course: String,
        #[arg(long, default_value = "courses")]
        courses: PathBuf,
    },
}

// ---------------------------------------------------------------------------------------------------------------
// Course definition files

#[derive(Debug, Deserialize)]
struct CourseToml {
    id: String,
    title: String,
    repo_name: String,
}

#[derive(Debug, Deserialize)]
struct ModuleToml {
    code: String,
    title: String,
    #[serde(default)]
    summary: String,
    /// Ids from `lectures.toml`: watch or read these before the module.
    #[serde(default)]
    lectures: Vec<String>,
    /// BusTub's own files this module ports.
    #[serde(default)]
    bustub: Vec<String>,
    /// Everything else worth reading: docs, books, papers, blogs, videos, other projects' code.
    #[serde(default)]
    resources: Vec<Resource>,
    /// Files that must arrive with this module although a later module's stage also touches them (see course_unlock.rs).
    #[serde(default)]
    files: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct Resource {
    /// docs · book · paper · blog · video · code · man
    kind: String,
    title: String,
    url: String,
}

#[derive(Debug, Deserialize)]
struct LecturesToml {
    #[serde(default)]
    lecture: Vec<Lecture>,
}

#[derive(Debug, Clone, Deserialize)]
struct Lecture {
    id: String,
    title: String,
    term: String,
    slides: String,
    notes: Option<String>,
    video: Option<String>,
}

#[derive(Debug, Deserialize)]
struct StageToml {
    id: String,
    title: String,
    /// learn · build · boss
    kind: String,
    /// very-easy · easy · medium · hard, as CodeCrafters labels its stages.
    difficulty: String,
    /// `bin` or `bin::filter`: a test binary, optionally only the tests whose name contains `filter`.
    tests: Vec<String>,
    /// A boss stage may pass before it starts: it is a milestone, not new code.
    #[serde(default)]
    retest: bool,
}

#[derive(Debug)]
struct Stage {
    def: StageToml,
    module: String,
    module_title: String,
    /// Lectures, reading and BusTub files of the stage's module, for the stage page.
    resources: String,
    readme: String,
    /// 1-based position in the whole course.
    rank: usize,
}

#[derive(Debug)]
struct Course {
    meta: CourseToml,
    stages: Vec<Stage>,
    /// module code -> the `files` its module.toml lists.
    module_files: BTreeMap<String, Vec<String>>,
}

impl Course {
    fn load(root: &Path) -> anyhow::Result<Course> {
        let meta: CourseToml = read_toml(&root.join("course.toml"))?;
        let mut stages = Vec::new();
        let mut module_files = BTreeMap::new();
        let lectures: Vec<Lecture> = match fs::read_to_string(root.join("lectures.toml")) {
            Ok(t) => toml::from_str::<LecturesToml>(&t).context("parsing lectures.toml")?.lecture,
            Err(_) => Vec::new(),
        };
        let modules = sorted_dirs(&root.join("modules"))?;
        for m in modules {
            let mt: ModuleToml = read_toml(&m.join("module.toml"))?;
            let mut resources = String::new();
            for id in &mt.lectures {
                let l = lectures.iter().find(|l| &l.id == id).with_context(|| format!("module {}: no lecture {id:?} in lectures.toml", mt.code))?;
                resources.push_str(&format!("  Lecture  {} (CMU 15-445, {})\n    slides  {}\n", l.title, l.term, l.slides));
                if let Some(n) = &l.notes {
                    resources.push_str(&format!("    notes   {n}\n"));
                }
                if let Some(v) = &l.video {
                    resources.push_str(&format!("    video   {v}\n"));
                }
            }
            for f in &mt.bustub {
                resources.push_str(&format!("  BusTub   https://github.com/cmu-db/bustub/blob/master/{f}\n"));
            }
            for kind in ["docs", "book", "man", "paper", "blog", "video", "code"] {
                for r in mt.resources.iter().filter(|r| r.kind == kind) {
                    resources.push_str(&format!("  {:<8} {}\n    {}\n", kind, r.title, r.url));
                }
            }
            for s in sorted_dirs(&m.join("stages"))? {
                let def: StageToml = read_toml(&s.join("stage.toml"))?;
                let readme = fs::read_to_string(s.join("stage.md"))
                    .with_context(|| format!("reading {}", s.join("stage.md").display()))?;
                if !matches!(def.kind.as_str(), "learn" | "build" | "boss") {
                    bail!("{}: kind must be learn, build or boss", def.id);
                }
                if !matches!(def.difficulty.as_str(), "very-easy" | "easy" | "medium" | "hard") {
                    bail!("{}: difficulty must be very-easy, easy, medium or hard", def.id);
                }
                if def.tests.is_empty() {
                    bail!("{}: a stage needs at least one test entry", def.id);
                }
                stages.push(Stage {
                    def,
                    module: mt.code.clone(),
                    module_title: mt.title.clone(),
                    resources: resources.clone(),
                    readme,
                    rank: 0,
                });
            }
            module_files.insert(mt.code.clone(), mt.files.clone());
            let _ = &mt.summary;
        }
        for (i, s) in stages.iter_mut().enumerate() {
            s.rank = i + 1;
        }
        let mut seen = HashMap::new();
        for s in &stages {
            if let Some(prev) = seen.insert(s.def.id.clone(), s.rank) {
                bail!("stage id {} is used twice (positions {prev} and {})", s.def.id, s.rank);
            }
        }
        Ok(Course { meta, stages, module_files })
    }

    fn stage(&self, id: &str) -> anyhow::Result<&Stage> {
        self.stages
            .iter()
            .find(|s| s.def.id == id)
            .with_context(|| format!("no stage {id:?}; `anneal course status` lists them"))
    }

    fn ranks(&self) -> HashMap<String, usize> {
        self.stages.iter().map(|s| (s.def.id.clone(), s.rank)).collect()
    }
}

fn read_toml<T: for<'de> Deserialize<'de>>(path: &Path) -> anyhow::Result<T> {
    let text = fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
    toml::from_str(&text).with_context(|| format!("parsing {}", path.display()))
}

fn sorted_dirs(dir: &Path) -> anyhow::Result<Vec<PathBuf>> {
    let mut v: Vec<PathBuf> = fs::read_dir(dir)
        .with_context(|| format!("reading {}", dir.display()))?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.is_dir())
        .collect();
    v.sort();
    Ok(v)
}

// ---------------------------------------------------------------------------------------------------------------
// Rendering the reference: @begin / @end regions

/// Renders one file for the state "stages up to `cutoff` are done".
///
/// A region is `// @begin <stage>` … `// @end`. Inside it, plain lines are the solution and `//~ ` lines are the stub that stands in
/// for it. A done region keeps its solution lines; a region that isn't done keeps its stub lines (with the `//~` removed).
/// Regions may nest (a stage that adds three lines inside a function another stage wrote): when the outer region isn't done,
/// everything inside it, nested regions included, is replaced by the outer stub.
fn render_text(text: &str, ranks: &HashMap<String, usize>, cutoff: usize, name: &str) -> anyhow::Result<String> {
    struct Frame {
        done: bool,
        id: String,
        at: usize,
    }
    let mut out = String::with_capacity(text.len());
    let mut stack: Vec<Frame> = Vec::new();
    for (n, line) in text.split_inclusive('\n').enumerate() {
        let body = line.trim_start();
        let marker = body.strip_prefix("//").or_else(|| body.strip_prefix('#')).map(|r| r.trim_start());
        if let Some(m) = marker {
            if let Some(id) = m.strip_prefix("@begin ") {
                let id = id.trim();
                let rank = *ranks.get(id).with_context(|| format!("{name}:{}: unknown stage {id:?}", n + 1))?;
                stack.push(Frame { done: rank <= cutoff, id: id.to_owned(), at: n + 1 });
                continue;
            }
            if m.trim_end() == "@end" {
                if stack.pop().is_none() {
                    bail!("{name}:{}: @end without @begin", n + 1);
                }
                continue;
            }
        }
        // Which frame decides what this line becomes: the outermost region that isn't done, else the innermost one.
        let Some(top) = stack.last() else {
            out.push_str(line);
            continue;
        };
        let first_undone = stack.iter().position(|f| !f.done);
        let indent = &line[..line.len() - body.len()];
        let stub = body.strip_prefix("//~").or_else(|| body.strip_prefix("#~")).map(|r| r.strip_prefix(' ').unwrap_or(r));
        match first_undone {
            // Everything in the stack is done: the solution lines of the innermost region.
            None => {
                if stub.is_none() {
                    out.push_str(line);
                }
            }
            // The innermost region is the first undone one: its stub lines. Deeper than that, the line is replaced.
            Some(i) if i == stack.len() - 1 => {
                if let Some(s) = stub {
                    out.push_str(indent);
                    out.push_str(s);
                }
            }
            Some(_) => {}
        }
        let _ = top;
    }
    if let Some(f) = stack.last() {
        bail!("{name}:{}: region {} is never closed", f.at, f.id);
    }
    Ok(out)
}

/// Writes the rendered repo into `out`, touching only files whose contents changed (so cargo's cache survives).
fn render_tree(reference: &Path, out: &Path, ranks: &HashMap<String, usize>, cutoff: usize) -> anyhow::Result<()> {
    fn walk(base: &Path, dir: &Path, out: &Path, ranks: &HashMap<String, usize>, cutoff: usize, keep: &mut Vec<PathBuf>) -> anyhow::Result<()> {
        for e in fs::read_dir(dir)? {
            let e = e?;
            let path = e.path();
            let name = e.file_name().to_string_lossy().into_owned();
            if matches!(name.as_str(), "target" | ".git" | ".DS_Store") {
                continue;
            }
            let rel = path.strip_prefix(base)?.to_path_buf();
            if path.is_dir() {
                walk(base, &path, out, ranks, cutoff, keep)?;
                continue;
            }
            let bytes = fs::read(&path)?;
            let data = match String::from_utf8(bytes.clone()) {
                Ok(text) if text.contains("@begin ") => render_text(&text, ranks, cutoff, &rel.display().to_string())?.into_bytes(),
                _ => bytes,
            };
            let dest = out.join(&rel);
            fs::create_dir_all(dest.parent().unwrap())?;
            if fs::read(&dest).map(|old| old != data).unwrap_or(true) {
                fs::write(&dest, &data)?;
            }
            keep.push(rel);
        }
        Ok(())
    }
    let mut keep = Vec::new();
    walk(reference, reference, out, ranks, cutoff, &mut keep)?;
    // Remove files that no longer exist in the reference (a renamed file), but never target/.git/.anneal.
    fn prune(base: &Path, dir: &Path, keep: &[PathBuf]) -> anyhow::Result<()> {
        for e in fs::read_dir(dir)? {
            let e = e?;
            let path = e.path();
            let name = e.file_name().to_string_lossy().into_owned();
            if matches!(name.as_str(), "target" | ".git" | ".anneal" | "Cargo.lock") {
                continue;
            }
            if path.is_dir() {
                prune(base, &path, keep)?;
            } else if !keep.contains(&path.strip_prefix(base)?.to_path_buf()) {
                fs::remove_file(&path)?;
            }
        }
        Ok(())
    }
    if out.exists() {
        prune(out, out, &keep)?;
    }
    Ok(())
}

// ---------------------------------------------------------------------------------------------------------------
// Running tests

#[derive(Debug, Clone)]
struct TestOutcome {
    name: String,
    ok: bool,
    /// The failure message (first lines of the test's stdout), if it failed.
    detail: String,
}

#[derive(Debug, Default)]
struct RunReport {
    tests: Vec<TestOutcome>,
    /// Compiler errors or a timeout, when no test ran.
    problem: Option<String>,
}

impl RunReport {
    fn passed(&self) -> bool {
        self.problem.is_none() && !self.tests.is_empty() && self.tests.iter().all(|t| t.ok)
    }
}

fn split_entry(entry: &str) -> (&str, Option<&str>) {
    match entry.split_once("::") {
        Some((bin, filter)) => (bin, Some(filter)),
        None => (entry, None),
    }
}

/// Runs the entries (`bin` or `bin::filter`) of several stages: one `cargo test` per binary, with all its filters.
fn run_entries(repo: &Path, entries: &[String], target_dir: Option<&Path>, timeout: Duration) -> RunReport {
    let mut by_bin: BTreeMap<&str, Vec<&str>> = BTreeMap::new();
    let mut whole: Vec<&str> = Vec::new();
    for e in entries {
        let (bin, filter) = split_entry(e);
        match filter {
            Some(f) => by_bin.entry(bin).or_default().push(f),
            None => whole.push(bin),
        }
    }
    let mut report = RunReport::default();
    let bins: Vec<&str> = by_bin.keys().copied().chain(whole.iter().copied()).collect();
    for bin in bins {
        let filters: &[&str] = if whole.contains(&bin) { &[] } else { &by_bin[bin] };
        let mut cmd = Command::new("cargo");
        cmd.current_dir(repo).args(["test", "--test", bin, "--"]);
        cmd.args(filters);
        cmd.env("RUST_BACKTRACE", "0").env("CARGO_TERM_COLOR", "never");
        if let Some(t) = target_dir {
            cmd.env("CARGO_TARGET_DIR", t);
        }
        match run_with_timeout(cmd, timeout) {
            Err(e) => {
                report.problem = Some(format!("{bin}: {e}"));
                return report;
            }
            Ok((stdout, stderr, code)) => {
                let before = report.tests.len();
                parse_tests(&stdout, &mut report.tests);
                if report.tests.len() == before {
                    // Nothing ran: a compile error, or the filter matched nothing.
                    let tail: Vec<&str> = stderr.lines().filter(|l| !l.trim().is_empty()).collect();
                    let shown = if tail.len() > 40 { &tail[..40] } else { &tail[..] };
                    report.problem = Some(if code == Some(0) {
                        format!("{bin}: no test matched {filters:?}")
                    } else {
                        format!("{bin}: the tests didn't compile or run\n{}", shown.join("\n"))
                    });
                    return report;
                }
            }
        }
    }
    report
}

fn run_with_timeout(mut cmd: Command, timeout: Duration) -> anyhow::Result<(String, String, Option<i32>)> {
    cmd.stdin(Stdio::null()).stdout(Stdio::piped()).stderr(Stdio::piped());
    let mut child = cmd.spawn().context("starting cargo")?;
    let mut out = child.stdout.take().unwrap();
    let mut err = child.stderr.take().unwrap();
    let t_out = std::thread::spawn(move || {
        let mut s = Vec::new();
        let _ = std::io::Read::read_to_end(&mut out, &mut s);
        String::from_utf8_lossy(&s).into_owned()
    });
    let t_err = std::thread::spawn(move || {
        let mut s = Vec::new();
        let _ = std::io::Read::read_to_end(&mut err, &mut s);
        String::from_utf8_lossy(&s).into_owned()
    });
    let start = Instant::now();
    let status = loop {
        if let Some(st) = child.try_wait()? {
            break st;
        }
        if start.elapsed() > timeout {
            let _ = child.kill();
            let _ = child.wait();
            bail!("timed out after {}s (a deadlock or an endless loop?)", timeout.as_secs());
        }
        std::thread::sleep(Duration::from_millis(40));
    };
    Ok((t_out.join().unwrap_or_default(), t_err.join().unwrap_or_default(), status.code()))
}

/// Reads libtest's output: `test a::b ... ok` lines, and the `---- a::b stdout ----` blocks of the failures.
fn parse_tests(stdout: &str, into: &mut Vec<TestOutcome>) {
    let mut details: HashMap<String, String> = HashMap::new();
    let mut current: Option<String> = None;
    let mut buf: Vec<&str> = Vec::new();
    for line in stdout.lines() {
        if let Some(rest) = line.strip_prefix("---- ").and_then(|r| r.strip_suffix(" stdout ----")) {
            if let Some(c) = current.take() {
                details.insert(c, buf.join("\n"));
            }
            buf.clear();
            current = Some(rest.to_owned());
        } else if line.starts_with("failures:") || line.starts_with("test result:") {
            if let Some(c) = current.take() {
                details.insert(c, buf.join("\n"));
            }
            buf.clear();
        } else if current.is_some() {
            buf.push(line);
        }
    }
    if let Some(c) = current.take() {
        details.insert(c, buf.join("\n"));
    }
    for line in stdout.lines() {
        let Some(rest) = line.strip_prefix("test ") else { continue };
        if let Some(name) = rest.strip_suffix(" ... ok") {
            into.push(TestOutcome { name: name.to_owned(), ok: true, detail: String::new() });
        } else if let Some(name) = rest.strip_suffix(" ... FAILED") {
            let detail = details.get(name).cloned().unwrap_or_default();
            into.push(TestOutcome { name: name.to_owned(), ok: false, detail });
        }
    }
}

// ---------------------------------------------------------------------------------------------------------------
// The learner's repo: state, hooks, commands

const STATE_DIR: &str = ".anneal";

#[derive(Debug, Default, Serialize, Deserialize)]
struct Progress {
    /// stage id -> when it first passed.
    passed: BTreeMap<String, Passed>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Passed {
    at: u64,
    commit: String,
    ms: u64,
}

#[derive(Debug, Deserialize)]
struct LocalConfig {
    #[allow(dead_code)]
    course: String,
    /// Fail the push when the current stage's tests fail.
    #[serde(default)]
    block_on_fail: bool,
}

fn state_path(repo: &Path, name: &str) -> PathBuf {
    repo.join(STATE_DIR).join(name)
}

fn find_repo() -> anyhow::Result<PathBuf> {
    let mut dir = std::env::current_dir()?;
    loop {
        if dir.join(STATE_DIR).join("course.toml").exists() {
            return Ok(dir);
        }
        if !dir.pop() {
            bail!("not inside a course repo (no {STATE_DIR}/course.toml); create one with `anneal course init bustub`");
        }
    }
}

fn load_progress(repo: &Path) -> Progress {
    fs::read_to_string(state_path(repo, "progress.json"))
        .ok()
        .and_then(|t| serde_json::from_str(&t).ok())
        .unwrap_or_default()
}

fn save_progress(repo: &Path, p: &Progress) -> anyhow::Result<()> {
    fs::write(state_path(repo, "progress.json"), serde_json::to_string_pretty(p)? + "\n")?;
    Ok(())
}

fn learner_course(repo: &Path) -> anyhow::Result<Course> {
    Course::load(&repo.join(STATE_DIR).join("course"))
}

fn current<'a>(course: &'a Course, progress: &Progress) -> Option<&'a Stage> {
    course.stages.iter().find(|s| !progress.passed.contains_key(&s.def.id))
}

fn head_commit(repo: &Path) -> String {
    Command::new("git")
        .current_dir(repo)
        .args(["rev-parse", "--short", "HEAD"])
        .output()
        .ok()
        .filter(|o| o.status.success())
        .map(|o| String::from_utf8_lossy(&o.stdout).trim().to_owned())
        .unwrap_or_else(|| "uncommitted".into())
}

pub fn run(cmd: CourseCmd) -> anyhow::Result<ExitCode> {
    match cmd {
        CourseCmd::Init { course, dir, courses } => init(&course, dir, &courses),
        CourseCmd::Login { url } => {
            course_sync::login(&url)?;
            Ok(ExitCode::SUCCESS)
        }
        CourseCmd::Lint { course, courses, all } => lint(&course, &courses, all),
        CourseCmd::Solutions { course, courses, out, stages } => solutions(&course, &courses, out, &stages),
        CourseCmd::Status => status(),
        CourseCmd::Show { stage } => show(stage.as_deref()),
        CourseCmd::Test { stage, all } => test(stage.as_deref(), all, false),
        CourseCmd::Next => next(),
        CourseCmd::Update { course, courses } => update(&course, &courses),
        CourseCmd::Hooks => {
            install_hooks(&find_repo()?)?;
            println!("hooks installed");
            Ok(ExitCode::SUCCESS)
        }
        CourseCmd::Hook { name } => match name.as_str() {
            "pre-push" => test(None, false, true),
            other => bail!("no hook {other:?}"),
        },
        CourseCmd::Build { stage, full, out, course, courses } => {
            let root = courses.join(&course);
            let c = Course::load(&root)?;
            let cutoff = if full {
                usize::MAX
            } else if let Some(s) = stage {
                c.stage(&s)?.rank
            } else {
                0
            };
            render_tree(&root.join("reference"), &out, &c.ranks(), cutoff)?;
            println!("rendered {} into {}", if full { "the full solution".to_owned() } else { format!("stage cutoff {cutoff}") }, out.display());
            Ok(ExitCode::SUCCESS)
        }
        CourseCmd::Template { course, courses } => {
            let root = courses.join(&course);
            let c = Course::load(&root)?;
            let out = root.join("template");
            render_tree(&root.join("reference"), &out, &c.ranks(), 0)?;
            let map = files_map_for(&c, &root.join("reference"))?;
            fs::write(out.join(course_unlock::FILES_JSON), serde_json::to_string_pretty(&map)? + "\n")?;
            println!("template written to {} ({} files tied to a module)", out.display(), map.len());
            Ok(ExitCode::SUCCESS)
        }
        CourseCmd::Verify { course, courses, stage, from, work } => verify(&course, &courses, stage.as_deref(), from.as_deref(), work),
    }
}

fn copy_dir(from: &Path, to: &Path) -> anyhow::Result<()> {
    fs::create_dir_all(to)?;
    for e in fs::read_dir(from)? {
        let e = e?;
        let name = e.file_name();
        if matches!(name.to_string_lossy().as_ref(), "target" | ".git" | ".DS_Store") {
            continue;
        }
        let (src, dst) = (e.path(), to.join(&name));
        if src.is_dir() {
            copy_dir(&src, &dst)?;
        } else {
            fs::copy(&src, &dst)?;
        }
    }
    Ok(())
}

/// Which module first needs each reference file (see course_unlock.rs).
fn files_map_for(course: &Course, reference: &Path) -> anyhow::Result<BTreeMap<String, String>> {
    let stage_module: HashMap<String, String> = course.stages.iter().map(|s| (s.def.id.clone(), s.module.clone())).collect();
    let mut boss_bins: HashMap<String, String> = HashMap::new();
    for s in course.stages.iter().filter(|s| s.def.kind == "boss") {
        for t in &s.def.tests {
            boss_bins.insert(split_entry(t).0.to_owned(), s.module.clone());
        }
    }
    course_unlock::file_modules(reference, &module_order(course), &stage_module, &course.module_files, &boss_bins)
}

// ---------------------------------------------------------------------------------------------------------------
// Progressive reveal (course_unlock.rs): the learner's repo shows only the modules reached so far.

fn module_order(course: &Course) -> Vec<String> {
    let mut v: Vec<String> = Vec::new();
    for s in &course.stages {
        if v.last() != Some(&s.module) {
            v.push(s.module.clone());
        }
    }
    v
}

/// The modules whose files the learner sees: every module up to and including the first one with an unpassed stage.
fn unlocked_modules(course: &Course, progress: &Progress) -> Vec<String> {
    let order = module_order(course);
    let current = current(course, progress).map(|s| s.module.clone());
    match current.and_then(|c| order.iter().position(|m| *m == c)) {
        Some(i) => order[..=i].to_vec(),
        None => order,
    }
}

fn load_files_map(template: &Path) -> BTreeMap<String, String> {
    fs::read_to_string(template.join(course_unlock::FILES_JSON)).ok().and_then(|t| serde_json::from_str(&t).ok()).unwrap_or_default()
}

#[derive(Debug, Default)]
struct Sync {
    added: usize,
    updated: usize,
    conflicts: Vec<PathBuf>,
}

/// Brings the visible template files into `repo`: new files are created, files you haven't edited are refreshed, files you have
/// edited are never overwritten (the new version goes next to yours as `.new`). `base` remembers what was handed out.
fn sync_files(repo: &Path, template: &Path, unlocked: &[String]) -> anyhow::Result<Sync> {
    let map = load_files_map(template);
    let files: Vec<PathBuf> = list_files(template)?;
    let vis = course_unlock::visible(&files, &map, unlocked, &|rel| fs::read_to_string(template.join(rel)).map(|t| course_unlock::only_declares(&t)).unwrap_or(true));
    let base = repo.join(STATE_DIR).join("base");
    let mut report = Sync::default();
    for rel in &vis {
        let raw = fs::read(template.join(rel))?;
        let new = if course_unlock::is_module_file(rel) {
            let text = String::from_utf8_lossy(&raw).into_owned();
            course_unlock::filter_mod(&text, rel.parent().unwrap_or(Path::new("")), &vis).into_bytes()
        } else {
            raw
        };
        let cur_path = repo.join(rel);
        let cur = fs::read(&cur_path).ok();
        let old = fs::read(base.join(rel)).ok();
        let mut hand_out = true;
        match (&cur, &old) {
            (None, _) => {
                fs::create_dir_all(cur_path.parent().unwrap())?;
                fs::write(&cur_path, &new)?;
                report.added += 1;
            }
            (Some(c), _) if *c == new => {}
            (Some(c), Some(o)) if c == o => {
                fs::write(&cur_path, &new)?;
                report.updated += 1;
            }
            (Some(_), Some(o)) if *o == new => {} // the template didn't change; the edit is yours
            (Some(_), _) => {
                let mut name = cur_path.clone().into_os_string();
                name.push(".new");
                fs::write(&name, &new)?;
                report.conflicts.push(rel.clone());
                hand_out = false;
            }
        }
        if hand_out {
            let b = base.join(rel);
            fs::create_dir_all(b.parent().unwrap())?;
            fs::write(b, &new)?;
        }
    }
    Ok(report)
}

/// After progress changed: brings in the files of any module that has just been reached.
fn maybe_unlock(repo: &Path, course: &Course, progress: &Progress) -> anyhow::Result<()> {
    let template = repo.join(STATE_DIR).join("template");
    if !template.is_dir() {
        return Ok(()); // a repo made before modules were revealed progressively: everything is already there
    }
    let unlocked = unlocked_modules(course, progress);
    let r = sync_files(repo, &template, &unlocked)?;
    if r.added > 0 {
        let latest = unlocked.last().cloned().unwrap_or_default();
        println!("\nModule {} unlocked: {} new files (stubs, and the tests for the stages in it).", latest.to_uppercase(), r.added);
    }
    for c in &r.conflicts {
        println!("  you edited {}: the new version is in {}.new (merge by hand)", c.display(), c.display());
    }
    Ok(())
}

/// Where the course files are: `courses/<id>` here, else the checkout this binary was built from, so `anneal course init bustub` works
/// from any directory after `cargo install --path crates/cli`.
fn course_root(courses: &Path, id: &str) -> PathBuf {
    let here = courses.join(id);
    if here.join("course.toml").exists() {
        return here;
    }
    let built_from = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../courses").join(id);
    if built_from.join("course.toml").exists() { built_from } else { here }
}

fn init(course_id: &str, dir: Option<PathBuf>, courses: &Path) -> anyhow::Result<ExitCode> {
    let root = course_root(courses, course_id);
    let course = Course::load(&root)?;
    if course.meta.id != course_id {
        bail!("{} says its id is {:?}", root.join("course.toml").display(), course.meta.id);
    }
    let template = root.join("template");
    if !template.is_dir() {
        bail!("{} has no template; run `anneal course template --course {course_id}` first", root.display());
    }
    let dir = dir.unwrap_or_else(|| PathBuf::from(&course.meta.repo_name));
    if dir.exists() && fs::read_dir(&dir)?.next().is_some() {
        bail!("{} already exists and isn't empty", dir.display());
    }
    // The whole template stays in .anneal/template; only the modules reached so far are in the working tree.
    copy_dir(&template, &dir.join(STATE_DIR).join("template"))?;
    sync_files(&dir, &dir.join(STATE_DIR).join("template"), &unlocked_modules(&course, &Progress::default()))?;
    // The learner's copy of the stage definitions, so the CLI works without the anneal checkout.
    let defs = dir.join(STATE_DIR).join("course");
    fs::create_dir_all(&defs)?;
    fs::copy(root.join("course.toml"), defs.join("course.toml"))?;
    if root.join("lectures.toml").exists() {
        fs::copy(root.join("lectures.toml"), defs.join("lectures.toml"))?;
    }
    copy_dir(&root.join("modules"), &defs.join("modules"))?;
    fs::write(
        state_path(&dir, "course.toml"),
        format!("course = \"{course_id}\"\n# Set to true to stop `git push` when the current stage's tests fail.\nblock_on_fail = false\n"),
    )?;
    save_progress(&dir, &Progress::default())?;
    let git = |args: &[&str]| Command::new("git").current_dir(&dir).args(args).stdout(Stdio::null()).stderr(Stdio::null()).status();
    if !dir.join(".git").exists() {
        git(&["init", "-q", "-b", "main"]).context("running git init")?;
    }
    install_hooks(&dir)?;
    git(&["add", "-A"])?;
    let committed = git(&["commit", "-q", "-m", "Start the course"]).map(|s| s.success()).unwrap_or(false);
    println!("Created {} ({} stages in {} modules).", dir.display(), course.stages.len(), count_modules(&course));
    if !committed {
        println!("(The first commit didn't happen: set git user.name and user.email, then `git commit -am start`.)");
    }
    println!("\n  cd {}\n  anneal course show      # read the first stage\n  anneal course test      # run its tests\n  git commit -am work && git push   # the hook runs the tests too", dir.display());
    Ok(ExitCode::SUCCESS)
}

/// Files of `dir` as relative paths.
fn list_files(dir: &Path) -> anyhow::Result<Vec<PathBuf>> {
    fn walk(base: &Path, dir: &Path, out: &mut Vec<PathBuf>) -> anyhow::Result<()> {
        for e in fs::read_dir(dir)? {
            let p = e?.path();
            if p.is_dir() {
                walk(base, &p, out)?;
            } else {
                out.push(p.strip_prefix(base)?.to_path_buf());
            }
        }
        Ok(())
    }
    let mut v = Vec::new();
    walk(dir, dir, &mut v)?;
    Ok(v)
}

/// `anneal course update`: new stages and files arrive; your edited files are never overwritten.
fn update(course_id: &str, courses: &Path) -> anyhow::Result<ExitCode> {
    let repo = find_repo()?;
    let root = course_root(courses, course_id);
    let template = root.join("template");
    if !template.is_dir() {
        bail!("{} has no template", root.display());
    }
    let kept = repo.join(STATE_DIR).join("template");
    if kept.exists() {
        fs::remove_dir_all(&kept)?;
    }
    copy_dir(&template, &kept)?;
    // The stage definitions and the base snapshot move forward.
    let defs = repo.join(STATE_DIR).join("course");
    if defs.exists() {
        fs::remove_dir_all(&defs)?;
    }
    fs::create_dir_all(&defs)?;
    fs::copy(root.join("course.toml"), defs.join("course.toml"))?;
    if root.join("lectures.toml").exists() {
        fs::copy(root.join("lectures.toml"), defs.join("lectures.toml"))?;
    }
    copy_dir(&root.join("modules"), &defs.join("modules"))?;
    let course = learner_course(&repo)?;
    let progress = load_progress(&repo);
    let Sync { added, updated, conflicts } = sync_files(&repo, &kept, &unlocked_modules(&course, &progress))?;
    println!("Updated: {added} new files, {updated} given files refreshed, {} stages in the course.", course.stages.len());
    for c in &conflicts {
        println!("  you edited {}: the new version is in {}.new (merge by hand)", c.display(), c.display());
    }
    println!("`anneal course status` shows where you are.");
    Ok(ExitCode::SUCCESS)
}

fn count_modules(c: &Course) -> usize {
    let mut m: Vec<&str> = c.stages.iter().map(|s| s.module.as_str()).collect();
    m.dedup();
    m.len()
}

fn install_hooks(repo: &Path) -> anyhow::Result<()> {
    let hooks = repo.join(".git").join("hooks");
    if !hooks.is_dir() {
        bail!("{} isn't a git repo", repo.display());
    }
    // The binary that installed the hook runs it, so the hook works without `anneal` being on the PATH.
    let exe = std::env::current_exe().ok().map(|p| p.display().to_string()).unwrap_or_else(|| "anneal".into());
    let script = format!("#!/bin/sh\n# Installed by `anneal course hooks`: runs the current stage's tests and records the result.\nif [ -x '{exe}' ]; then exec '{exe}' course hook pre-push; else exec anneal course hook pre-push; fi\n");
    let path = hooks.join("pre-push");
    fs::write(&path, script)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        fs::set_permissions(&path, fs::Permissions::from_mode(0o755))?;
    }
    Ok(())
}

fn status() -> anyhow::Result<ExitCode> {
    let repo = find_repo()?;
    let course = learner_course(&repo)?;
    let progress = load_progress(&repo);
    println!("{}", course.meta.title);
    let cur = current(&course, &progress).map(|s| s.def.id.clone());
    let mut last_module = String::new();
    for s in &course.stages {
        if s.module != last_module {
            let total = course.stages.iter().filter(|x| x.module == s.module).count();
            let done = course.stages.iter().filter(|x| x.module == s.module && progress.passed.contains_key(&x.def.id)).count();
            println!("\n{}  {}  ({done}/{total})", s.module, s.module_title);
            last_module = s.module.clone();
        }
        let mark = if progress.passed.contains_key(&s.def.id) {
            "✓"
        } else if Some(&s.def.id) == cur.as_ref() {
            "→"
        } else {
            " "
        };
        println!("  {mark} {:<8} {:<9} {}", s.def.id, s.def.difficulty, s.def.title);
    }
    match cur {
        Some(id) => println!("\nCurrent: {id}. `anneal course show` to read it, `anneal course test` to run it."),
        None => println!("\nEvery stage is done."),
    }
    Ok(ExitCode::SUCCESS)
}

fn show(stage: Option<&str>) -> anyhow::Result<ExitCode> {
    let repo = find_repo()?;
    let course = learner_course(&repo)?;
    let progress = load_progress(&repo);
    let s = match stage {
        Some(id) => course.stage(id)?,
        None => current(&course, &progress).context("every stage is done")?,
    };
    print_stage(s);
    Ok(ExitCode::SUCCESS)
}

fn difficulty_label(d: &str) -> &'static str {
    match d {
        "very-easy" => "Very easy · under 5 minutes",
        "easy" => "Easy · 5-10 minutes",
        "medium" => "Medium · 30 minutes to 1 hour",
        _ => "Hard · more than 1 hour",
    }
}

fn print_stage(s: &Stage) {
    println!("{} · {}\nStage {}: {}\n{}  [{}]\n", s.module, s.module_title, s.def.id, s.def.title, difficulty_label(&s.def.difficulty), s.def.kind);
    println!("{}", s.readme.trim_end());
    println!("\nYour way: the tests call only the public items named above. How you build the inside is up to you; change the given structs and helpers if you want a different design.");
    if !s.resources.is_empty() {
        println!("\nModule resources\n{}", s.resources.trim_end());
    }
    println!("\nTests: {}", s.def.tests.iter().map(|t| format!("cargo test --test {}", t.replace("::", " -- "))).collect::<Vec<_>>().join("   "));
}

fn next() -> anyhow::Result<ExitCode> {
    let repo = find_repo()?;
    let course = learner_course(&repo)?;
    let progress = load_progress(&repo);
    maybe_unlock(&repo, &course, &progress)?;
    match current(&course, &progress) {
        Some(s) => {
            print_stage(s);
            Ok(ExitCode::SUCCESS)
        }
        None => {
            println!("That was the last stage. Nice work.");
            Ok(ExitCode::SUCCESS)
        }
    }
}

fn test(stage: Option<&str>, all: bool, hook: bool) -> anyhow::Result<ExitCode> {
    let repo = find_repo()?;
    let course = learner_course(&repo)?;
    let mut progress = load_progress(&repo);
    let cfg: LocalConfig = read_toml(&state_path(&repo, "course.toml"))?;
    let target = match stage {
        Some(id) => course.stage(id)?,
        None => match current(&course, &progress) {
            Some(s) => s,
            None => {
                println!("Every stage is done.");
                return Ok(ExitCode::SUCCESS);
            }
        },
    };
    println!("Stage {} · {}\n", target.def.id, target.def.title);
    let started = Instant::now();
    let report = run_entries(&repo, &target.def.tests, None, Duration::from_secs(180));
    print_report(&report);
    let ok = report.passed();
    {
        let tests: Vec<(String, bool, String)> = report.tests.iter().map(|t| (t.name.clone(), t.ok, t.detail.lines().filter(|l| !l.trim().is_empty()).take(6).collect::<Vec<_>>().join("\n"))).collect();
        course_sync::report_run(&course.meta.id, &target.def.id, &tests, report.problem.as_deref(), &head_commit(&repo), started.elapsed().as_millis() as u64);
    }
    if !ok {
        println!("\nNot yet. `anneal course show {}` has the task and hints.", target.def.id);
        return Ok(if hook && cfg.block_on_fail { ExitCode::FAILURE } else { ExitCode::SUCCESS });
    }
    let ms = started.elapsed().as_millis() as u64;
    // Regression: everything that already passed must still pass.
    let earlier: Vec<String> = course
        .stages
        .iter()
        .filter(|s| s.rank < target.rank && (all || progress.passed.contains_key(&s.def.id)))
        .flat_map(|s| s.def.tests.clone())
        .collect();
    if !earlier.is_empty() {
        let mut uniq = earlier;
        uniq.sort();
        uniq.dedup();
        let reg = run_entries(&repo, &uniq, None, Duration::from_secs(300));
        let broken: Vec<&TestOutcome> = reg.tests.iter().filter(|t| !t.ok).collect();
        if let Some(p) = &reg.problem {
            println!("\nRegression run failed: {p}");
            return Ok(if hook && cfg.block_on_fail { ExitCode::FAILURE } else { ExitCode::SUCCESS });
        }
        if !broken.is_empty() {
            println!("\nThis stage passes, but you broke earlier stages:");
            for t in broken {
                println!("  ✗ {}", t.name);
            }
            return Ok(if hook && cfg.block_on_fail { ExitCode::FAILURE } else { ExitCode::SUCCESS });
        }
        println!("\nEarlier stages: {} tests still pass.", reg.tests.len());
    }
    if !progress.passed.contains_key(&target.def.id) {
        let at = SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0);
        progress.passed.insert(target.def.id.clone(), Passed { at, commit: head_commit(&repo), ms });
        save_progress(&repo, &progress)?;
        println!("\n✓ Stage {} complete.", target.def.id);
        maybe_unlock(&repo, &course, &progress)?;
        match current(&course, &progress) {
            Some(n) => println!("Next: {} · {}  (`anneal course next`)", n.def.id, n.def.title),
            None => println!("That was the last stage."),
        }
    } else {
        println!("\n✓ Stage {} passes (already recorded).", target.def.id);
    }
    Ok(ExitCode::SUCCESS)
}

fn print_report(r: &RunReport) {
    for t in &r.tests {
        let short = t.name.rsplit("::").next().unwrap_or(&t.name);
        if t.ok {
            println!("  ✓ {short}");
        } else {
            println!("  ✗ {short}");
            for l in t.detail.lines().filter(|l| !l.trim().is_empty()).take(8) {
                println!("      {l}");
            }
        }
    }
    if let Some(p) = &r.problem {
        println!("\n{p}");
    }
}

// ---------------------------------------------------------------------------------------------------------------
// Authoring: lint (docs/COURSE_STANDARDS.md)

/// The bullet count of each `### Tests` block in a stage's markdown (outside code fences).
fn tests_bullets(md: &str) -> Vec<usize> {
    let (mut in_tests, mut fence, mut n) = (false, false, 0);
    let mut blocks = Vec::new();
    for line in md.lines() {
        if line.trim_start().starts_with("```") {
            fence = !fence;
        }
        if fence {
            continue;
        }
        if let Some(h) = line.strip_prefix("## ").or_else(|| line.strip_prefix("### ")) {
            if in_tests {
                blocks.push(n);
            }
            n = 0;
            in_tests = h.trim().to_lowercase() == "tests";
            continue;
        }
        if in_tests && (line.starts_with("- ") || line.starts_with("* ")) {
            n += 1;
        }
    }
    if in_tests {
        blocks.push(n);
    }
    blocks
}

fn lint(course_id: &str, courses: &Path, all: bool) -> anyhow::Result<ExitCode> {
    use anneal_content::course::Course as Def;
    let root = courses.join(course_id);
    let def = if all { Def::load_all(&root) } else { Def::load(&root) }.map_err(|e| anyhow::anyhow!("{e}"))?;
    let mut problems = Vec::new();
    let mut checked = 0;
    for m in &def.modules {
        if !(6..=10).contains(&m.stages.len()) {
            println!("note  {}: {} stages (6 to 10 is the sweet spot; not a hard limit)", m.code, m.stages.len());
        }
        for st in &m.stages {
            if st.kind == "boss" {
                continue;
            }
            checked += 1;
            let id = &st.id;
            if st.learn.len() < 2 {
                problems.push(format!("{id}: `learn` needs at least 2 entries (what this stage teaches)"));
            }
            if st.concepts.is_empty() {
                problems.push(format!("{id}: link at least one concept article (`concepts = [...]`)"));
            }
            if !st.sections.iter().any(|s| s.id == "performance") {
                problems.push(format!("{id}: add a `## Performance` section"));
            }
            if st.hints.len() < 2 {
                problems.push(format!("{id}: {} hint(s); write at least 2 (design, then the trap, then the invariant)", st.hints.len()));
            }
            let blocks: Vec<usize> = std::iter::once(st.intro.as_str()).chain(st.sections.iter().map(|s| s.md.as_str())).flat_map(tests_bullets).collect();
            let total: usize = blocks.iter().sum();
            if blocks.iter().any(|&b| b > 4) || total > 8 {
                problems.push(format!("{id}: Tests text has {total} bullets ({blocks:?}); summarise the key behaviours: at most 4 per Tests block and 8 per stage (every test is listed by name in Last run)"));
            }
        }
    }
    for p in &problems {
        println!("FAIL  {p}");
    }
    println!("\n{checked} stages checked, {} problems", problems.len());
    Ok(if problems.is_empty() { ExitCode::SUCCESS } else { ExitCode::FAILURE })
}

// ---------------------------------------------------------------------------------------------------------------
// Authoring: solutions

/// Renders every text file of the reference for each stage and uploads (or writes) the per-stage diffs.
fn solutions(course_id: &str, courses: &Path, out: Option<PathBuf>, only: &[String]) -> anyhow::Result<ExitCode> {
    let root = courses.join(course_id);
    let course = Course::load(&root)?;
    let ranks = course.ranks();
    let reference = root.join("reference");
    if !reference.is_dir() {
        bail!("{} has no reference/ (it is kept out of the public repo; see docs/BUSTUB.md §7)", root.display());
    }
    fn files(base: &Path, dir: &Path, out: &mut Vec<PathBuf>) -> anyhow::Result<()> {
        let mut entries: Vec<_> = fs::read_dir(dir)?.filter_map(|e| e.ok()).collect();
        entries.sort_by_key(|e| e.file_name());
        for e in entries {
            let name = e.file_name().to_string_lossy().into_owned();
            if matches!(name.as_str(), "target" | ".git" | ".DS_Store") {
                continue;
            }
            let p = e.path();
            if p.is_dir() {
                files(base, &p, out)?;
            } else if p.extension().is_some_and(|x| x == "rs") && !p.strip_prefix(base)?.starts_with("tests") {
                out.push(p.strip_prefix(base)?.to_path_buf());
            }
        }
        Ok(())
    }
    let mut paths = Vec::new();
    files(&reference, &reference, &mut paths)?;
    let texts: Vec<(String, String)> =
        paths.iter().filter_map(|p| fs::read_to_string(reference.join(p)).ok().filter(|t| t.contains("@begin ")).map(|t| (p.display().to_string(), t))).collect();
    let render = |cutoff: usize| -> anyhow::Result<BTreeMap<String, String>> {
        texts.iter().map(|(name, t)| Ok((name.clone(), render_text(t, &ranks, cutoff, name)?))).collect()
    };
    let diffs = course_sync::solution_diffs(&ranks, &render)?;
    match out {
        Some(path) => {
            fs::write(&path, serde_json::to_string_pretty(&diffs)? + "\n")?;
            println!("Wrote {} stage solutions to {}", diffs.values().filter(|v| !v.is_empty()).count(), path.display());
        }
        None => course_sync::push_solutions(&course.meta.id, &diffs, if only.is_empty() { None } else { Some(only) })?,
    }
    Ok(ExitCode::SUCCESS)
}

// ---------------------------------------------------------------------------------------------------------------
// Authoring: verify

fn verify(course_id: &str, courses: &Path, only: Option<&str>, from: Option<&str>, work: Option<PathBuf>) -> anyhow::Result<ExitCode> {
    let root = courses.join(course_id);
    let course = Course::load(&root)?;
    let ranks = course.ranks();
    let reference = root.join("reference");
    if !reference.is_dir() {
        bail!("{} has no reference/ (it is kept out of the public repo; see docs/BUSTUB.md §7)", root.display());
    }
    let work = work.unwrap_or_else(|| std::env::temp_dir().join(format!("anneal-course-{course_id}")));
    let target = work.join("target");
    let repo = work.join("repo");
    fs::create_dir_all(&repo)?;
    let first = match from {
        Some(id) => course.stage(id)?.rank,
        None => 1,
    };
    let mut problems = 0;
    for s in &course.stages {
        if s.rank < first {
            continue;
        }
        if let Some(id) = only
            && s.def.id != id
        {
            continue;
        }
        let t0 = Instant::now();
        // Before: the stage's tests must fail (unless a boss).
        render_tree(&reference, &repo, &ranks, s.rank - 1)?;
        let before = run_entries(&repo, &s.def.tests, Some(&target), Duration::from_secs(120));
        // After: they must pass, and so must everything before.
        render_tree(&reference, &repo, &ranks, s.rank)?;
        let after = run_entries(&repo, &s.def.tests, Some(&target), Duration::from_secs(120));
        let mut notes: Vec<String> = Vec::new();
        if !after.passed() {
            notes.push(format!(
                "tests fail with the solution: {}",
                after.problem.clone().unwrap_or_else(|| after.tests.iter().filter(|t| !t.ok).map(|t| t.name.clone()).collect::<Vec<_>>().join(", "))
            ));
        }
        if s.def.kind != "boss" && after.tests.len() < 5 {
            notes.push(format!("{} test(s); a stage needs at least 5, each checking a distinct behaviour (docs/COURSE_STANDARDS.md)", after.tests.len()));
        }
        if !s.def.retest && before.problem.is_none() && !before.tests.is_empty() && before.tests.iter().all(|t| t.ok) {
            notes.push("all tests already pass before the stage (the stub isn't doing its job)".into());
        }
        if before.problem.as_deref().is_some_and(|p| p.contains("didn't compile")) {
            notes.push("the stub state doesn't compile".into());
        }
        let mut earlier: Vec<String> = course.stages.iter().filter(|x| x.rank < s.rank).flat_map(|x| x.def.tests.clone()).collect();
        earlier.sort();
        earlier.dedup();
        if notes.is_empty() && !earlier.is_empty() {
            let reg = run_entries(&repo, &earlier, Some(&target), Duration::from_secs(300));
            if !reg.passed() {
                notes.push(format!(
                    "earlier tests break: {}",
                    reg.problem.clone().unwrap_or_else(|| reg.tests.iter().filter(|t| !t.ok).map(|t| t.name.clone()).collect::<Vec<_>>().join(", "))
                ));
            }
        }
        if notes.is_empty() {
            println!("ok    {:<8} {:<5} {:>3} tests  {:>5.1}s  {}", s.def.id, s.def.kind, after.tests.len(), t0.elapsed().as_secs_f64(), s.def.title);
        } else {
            problems += 1;
            println!("FAIL  {:<8} {}", s.def.id, s.def.title);
            for n in notes {
                println!("        {n}");
            }
        }
    }
    if (only.is_none() && from.is_none()) || only == Some("unlock") {
        problems += verify_unlock_states(&course, &reference, &repo, &work, &target, &ranks)?;
    }
    println!("\n{} stages, {problems} problems", course.stages.len());
    Ok(if problems == 0 { ExitCode::SUCCESS } else { ExitCode::FAILURE })
}

/// Every module's unlock state must compile (and so must its tests): the repo a learner has when they reach module k, with the
/// stubs of module k, shows only the files of modules 1..=k. Catches a file that is revealed later than something that names it.
fn verify_unlock_states(course: &Course, reference: &Path, full: &Path, work: &Path, target: &Path, ranks: &HashMap<String, usize>) -> anyhow::Result<usize> {
    let map = files_map_for(course, reference)?;
    let order = module_order(course);
    let shown = work.join("unlock-repo");
    let mut problems = 0;
    for (k, code) in order.iter().enumerate() {
        let cutoff = if k == 0 { 0 } else { course.stages.iter().filter(|s| order[..k].contains(&s.module)).map(|s| s.rank).max().unwrap_or(0) };
        render_tree(reference, full, ranks, cutoff)?;
        let files: Vec<PathBuf> = list_files(full)?.into_iter().filter(|p| !p.starts_with("target")).collect();
        let vis = course_unlock::visible(&files, &map, &order[..=k], &|rel| fs::read_to_string(full.join(rel)).map(|t| course_unlock::only_declares(&t)).unwrap_or(true));
        if shown.exists() {
            fs::remove_dir_all(&shown)?;
        }
        for rel in &vis {
            let dest = shown.join(rel);
            fs::create_dir_all(dest.parent().unwrap())?;
            let raw = fs::read(full.join(rel))?;
            if course_unlock::is_module_file(rel) {
                let text = String::from_utf8_lossy(&raw).into_owned();
                fs::write(&dest, course_unlock::filter_mod(&text, rel.parent().unwrap_or(Path::new("")), &vis))?;
            } else {
                fs::write(&dest, raw)?;
            }
        }
        let t0 = Instant::now();
        let mut cmd = Command::new("cargo");
        cmd.current_dir(&shown).args(["test", "--no-run"]).env("CARGO_TARGET_DIR", target).env("CARGO_TERM_COLOR", "never");
        let (_, stderr, status) = run_with_timeout(cmd, Duration::from_secs(300)).map_err(|e| anyhow::anyhow!("{e}"))?;
        if status == Some(0) {
            println!("ok    unlock {:<4} {:>3} files visible  {:>5.1}s", code, vis.len(), t0.elapsed().as_secs_f64());
        } else {
            problems += 1;
            println!("FAIL  unlock {code}: the repo a learner has on reaching this module doesn't compile");
            for l in stderr.lines().filter(|l| l.starts_with("error")).take(6) {
                println!("        {l}");
            }
        }
    }
    Ok(problems)
}
