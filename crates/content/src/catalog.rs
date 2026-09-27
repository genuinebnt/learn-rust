use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};

use crate::model::{Mode, ProblemFile, Section, StageDef, Status, Tier, TrackFile};

/// Everything under `content/tracks`, loaded and validated.
#[derive(Debug, Default)]
pub struct Catalog {
    /// Sorted by section, then by the section's recommended order.
    pub tracks: Vec<Track>,
}

#[derive(Debug)]
pub struct Track {
    /// Folder name, e.g. `d9-graphs`.
    pub slug: String,
    pub code: String,
    pub name: String,
    pub section: Section,
    pub tier: Tier,
    pub order: u32,
    pub summary: String,
    pub stages: Vec<StageDef>,
    /// Sorted by `order`.
    pub problems: Vec<Problem>,
}

#[derive(Debug)]
pub struct Problem {
    /// Globally unique: `<track code lowercased>-<slug>`, e.g. `d9-network-delay-time`.
    pub id: String,
    pub meta: ProblemFile,
    pub dir: PathBuf,
    pub files: ProblemFiles,
}

/// File contents; `None` when the file is absent (allowed for drafts).
#[derive(Debug, Default)]
pub struct ProblemFiles {
    pub statement: Option<String>,
    pub starter: Option<String>,
    pub solution: Option<String>,
    pub visible_tests: Option<String>,
    pub hidden_tests: Option<String>,
    /// `wrong/<name>.rs`: plausible but incorrect solutions the tests must reject, as `(name, code)`
    /// sorted by name. Only `anneal verify` reads them.
    pub wrong: Vec<(String, String)>,
}

/// A problem with the content, reported with the file it was found in.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Issue {
    pub path: PathBuf,
    pub message: String,
}

impl std::fmt::Display for Issue {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}: {}", self.path.display(), self.message)
    }
}

#[derive(Debug, thiserror::Error)]
pub enum LoadError {
    #[error("cannot read content directory {path}: {source}")]
    Io {
        path: PathBuf,
        #[source]
        source: std::io::Error,
    },
}

/// The catalog plus every issue found. Parts that failed to parse are left out
/// of the catalog and reported as issues, so one bad file never hides the rest.
#[derive(Debug)]
pub struct Loaded {
    pub catalog: Catalog,
    pub issues: Vec<Issue>,
}

impl Catalog {
    /// Loads `<root>/tracks/*`. `root` is the `content/` directory.
    pub fn load(root: &Path) -> Result<Loaded, LoadError> {
        let tracks_dir = root.join("tracks");
        let mut issues = Vec::new();
        let mut tracks = Vec::new();
        for dir in sorted_subdirs(&tracks_dir)? {
            if let Some(track) = load_track(&dir, &mut issues)? {
                tracks.push(track);
            }
        }
        tracks.sort_by_key(|t| (section_rank(t.section), t.order));
        check_catalog(&tracks, &mut issues);
        Ok(Loaded {
            catalog: Catalog { tracks },
            issues,
        })
    }

    pub fn track(&self, slug_or_code: &str) -> Option<&Track> {
        self.tracks
            .iter()
            .find(|t| t.slug == slug_or_code || t.code.eq_ignore_ascii_case(slug_or_code))
    }

    pub fn problem(&self, id: &str) -> Option<(&Track, &Problem)> {
        self.tracks
            .iter()
            .find_map(|t| t.problems.iter().find(|p| p.id == id).map(|p| (t, p)))
    }
}

impl Track {
    pub fn stage(&self, slug: &str) -> Option<&StageDef> {
        self.stages.iter().find(|s| s.slug == slug)
    }
}

fn section_rank(s: Section) -> u8 {
    match s {
        Section::Dsa => 0,
        Section::Language => 1,
        Section::StandardLibrary => 2,
        Section::Concurrency => 3,
        Section::Systems => 4,
        Section::Backend => 5,
        Section::Design => 6,
    }
}

fn sorted_subdirs(dir: &Path) -> Result<Vec<PathBuf>, LoadError> {
    let io = |source| LoadError::Io {
        path: dir.to_path_buf(),
        source,
    };
    let mut dirs = Vec::new();
    for entry in fs::read_dir(dir).map_err(io)? {
        let entry = entry.map_err(io)?;
        if entry.file_type().map_err(io)?.is_dir() {
            dirs.push(entry.path());
        }
    }
    dirs.sort();
    Ok(dirs)
}

fn read_toml<T: serde::de::DeserializeOwned>(path: &Path, issues: &mut Vec<Issue>) -> Option<T> {
    let text = match fs::read_to_string(path) {
        Ok(t) => t,
        Err(e) => {
            issues.push(issue(path, format!("cannot read: {e}")));
            return None;
        }
    };
    match toml::from_str(&text) {
        Ok(v) => Some(v),
        Err(e) => {
            issues.push(issue(path, format!("invalid TOML: {}", e.message())));
            None
        }
    }
}

fn read_optional(path: &Path) -> Option<String> {
    fs::read_to_string(path).ok()
}

/// Every `<name>.rs` in `dir`, sorted by name; empty when the folder is absent.
fn read_wrong(dir: &Path) -> Vec<(String, String)> {
    let Ok(entries) = fs::read_dir(dir) else { return Vec::new() };
    let mut out: Vec<(String, String)> = entries
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|x| x == "rs"))
        .filter_map(|p| Some((p.file_stem()?.to_string_lossy().into_owned(), fs::read_to_string(&p).ok()?)))
        .collect();
    out.sort();
    out
}

fn issue(path: &Path, message: impl Into<String>) -> Issue {
    Issue {
        path: path.to_path_buf(),
        message: message.into(),
    }
}

fn load_track(dir: &Path, issues: &mut Vec<Issue>) -> Result<Option<Track>, LoadError> {
    let file = dir.join("track.toml");
    let Some(meta) = read_toml::<TrackFile>(&file, issues) else {
        return Ok(None);
    };
    let slug = dir_name(dir);
    check_track(&slug, &meta, &file, issues);

    let mut problems = Vec::new();
    let problems_dir = dir.join("problems");
    if problems_dir.is_dir() {
        for pdir in sorted_subdirs(&problems_dir)? {
            if let Some(p) = load_problem(&pdir, &meta, issues) {
                problems.push(p);
            }
        }
    }
    problems.sort_by_key(|p| p.meta.order);
    check_problem_order(&problems, &meta, &file, issues);

    Ok(Some(Track {
        slug,
        code: meta.code,
        name: meta.name,
        section: meta.section,
        tier: meta.tier,
        order: meta.order,
        summary: meta.summary,
        stages: meta.stages,
        problems,
    }))
}

fn dir_name(dir: &Path) -> String {
    dir.file_name()
        .map(|n| n.to_string_lossy().into_owned())
        .unwrap_or_default()
}

fn check_track(slug: &str, meta: &TrackFile, file: &Path, issues: &mut Vec<Issue>) {
    let code = meta.code.as_bytes();
    let well_formed = code.len() >= 2
        && code[0] == meta.section.letter() as u8
        && code[1..].iter().all(u8::is_ascii_digit);
    if !well_formed {
        issues.push(issue(
            file,
            format!(
                "code {:?} must be the section letter {} followed by digits",
                meta.code,
                meta.section.letter()
            ),
        ));
    }
    let prefix = format!("{}-", meta.code.to_ascii_lowercase());
    if !slug.starts_with(&prefix) {
        issues.push(issue(
            file,
            format!("folder {slug:?} must start with {prefix:?}"),
        ));
    }
    if meta.stages.is_empty() {
        issues.push(issue(file, "a track needs at least one stage"));
    }
    let mut seen = HashSet::new();
    for s in &meta.stages {
        if !seen.insert(s.slug.as_str()) {
            issues.push(issue(
                file,
                format!("stage slug {:?} is used twice", s.slug),
            ));
        }
    }
    // Tracks climb from easy to hard: a stage may never be easier than the one before it.
    for pair in meta.stages.windows(2) {
        if pair[1].band < pair[0].band {
            issues.push(issue(
                file,
                format!("stage {:?} ({:?}) comes after {:?} ({:?}); stages must run easy → medium → hard", pair[1].slug, pair[1].band, pair[0].slug, pair[0].band),
            ));
        }
    }
}

fn load_problem(dir: &Path, track: &TrackFile, issues: &mut Vec<Issue>) -> Option<Problem> {
    let file = dir.join("problem.toml");
    let meta = read_toml::<ProblemFile>(&file, issues)?;
    let files = ProblemFiles {
        statement: read_optional(&dir.join("statement.md")),
        starter: read_optional(&dir.join("starter.rs")),
        solution: read_optional(&dir.join("solution.rs")),
        visible_tests: read_optional(&dir.join("tests/visible.rs")),
        hidden_tests: read_optional(&dir.join("tests/hidden.rs")),
        wrong: read_wrong(&dir.join("wrong")),
    };
    check_problem(dir, &meta, &files, track, &file, issues);
    Some(Problem {
        id: format!("{}-{}", track.code.to_ascii_lowercase(), meta.slug),
        meta,
        dir: dir.to_path_buf(),
        files,
    })
}

fn check_problem(
    dir: &Path,
    meta: &ProblemFile,
    files: &ProblemFiles,
    track: &TrackFile,
    file: &Path,
    issues: &mut Vec<Issue>,
) {
    if dir_name(dir) != meta.slug {
        issues.push(issue(
            file,
            format!(
                "slug {:?} must match the folder name {:?}",
                meta.slug,
                dir_name(dir)
            ),
        ));
    }
    if !track.stages.iter().any(|s| s.slug == meta.stage) {
        issues.push(issue(
            file,
            format!("stage {:?} is not defined in track.toml", meta.stage),
        ));
    }
    if meta.rules.is_some() && meta.mode != Mode::Fix {
        issues.push(issue(file, "rules only apply to fix-this problems"));
    }
    if meta.status == Status::Draft {
        return;
    }
    let required = [
        ("statement.md", &files.statement),
        ("starter.rs", &files.starter),
        ("solution.rs", &files.solution),
        ("tests/visible.rs", &files.visible_tests),
        ("tests/hidden.rs", &files.hidden_tests),
    ];
    for (name, content) in required {
        if content.as_deref().is_none_or(|c| c.trim().is_empty()) {
            issues.push(issue(file, format!("ready problems need {name}")));
        }
    }
    if !(1..=3).contains(&meta.hints.len()) {
        issues.push(issue(
            file,
            format!("ready problems need 1–3 hints, found {}", meta.hints.len()),
        ));
    }
    if meta.solution.is_none() {
        issues.push(issue(
            file,
            "ready problems need [solution] notes with explanation and complexity",
        ));
    }
    if meta.follow_up.is_none() {
        issues.push(issue(
            file,
            "ready problems need an interview follow_up question",
        ));
    }
}

fn check_problem_order(
    problems: &[Problem],
    track: &TrackFile,
    file: &Path,
    issues: &mut Vec<Issue>,
) {
    let mut orders: HashMap<u32, &str> = HashMap::new();
    for p in problems {
        if let Some(other) = orders.insert(p.meta.order, &p.meta.slug) {
            issues.push(issue(
                file,
                format!(
                    "order {} is used by both {:?} and {:?}",
                    p.meta.order, other, p.meta.slug
                ),
            ));
        }
    }
    // Problems sorted by `order` must walk the stages in track order.
    let stage_index = |slug: &str| track.stages.iter().position(|s| s.slug == slug);
    let mut last: Option<(usize, &str)> = None;
    for p in problems {
        let Some(idx) = stage_index(&p.meta.stage) else {
            continue;
        };
        if let Some((prev, prev_slug)) = last
            && idx < prev
        {
            issues.push(issue(
                file,
                format!(
                    "problem {:?} (stage {:?}) is ordered after {:?}, which is in a later stage",
                    p.meta.slug, p.meta.stage, prev_slug
                ),
            ));
        }
        last = Some((idx, &p.meta.slug));
    }
    // Inside a stage, problems run easy → hard too.
    for pair in problems.windows(2) {
        let (a, b) = (&pair[0].meta, &pair[1].meta);
        if a.stage == b.stage && b.level < a.level {
            issues.push(issue(
                file,
                format!("problem {:?} ({:?}) comes after {:?} ({:?}) in stage {:?}; problems in a stage must run easy → hard", b.slug, b.level, a.slug, a.level, a.stage),
            ));
        }
    }
}

fn check_catalog(tracks: &[Track], issues: &mut Vec<Issue>) {
    let mut codes = HashSet::new();
    let mut ids = HashSet::new();
    for t in tracks {
        if !codes.insert(t.code.as_str()) {
            issues.push(Issue {
                path: PathBuf::from(&t.slug),
                message: format!("track code {} is used twice", t.code),
            });
        }
        for p in &t.problems {
            if !ids.insert(p.id.as_str()) {
                issues.push(issue(&p.dir, format!("problem id {} is used twice", p.id)));
            }
        }
    }
}
