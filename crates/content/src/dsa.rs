//! The NeetCode lists as DSA tracks, loaded from `content/dsa/problems.json` (built by `tools/neetcode/build.py`).
//!
//! These problems aren't run in anneal: you solve them on LeetCode and log how it went. They load as ordinary tracks
//! (one per NeetCode pattern, ids `lc-<leetcode slug>`) so that streaks, reviews, readiness and the Progress pages
//! treat them like any other problem. [`Problem::dsa`](crate::Problem::dsa) carries what only they have.

use std::collections::BTreeMap;
use std::path::Path;

use serde::{Deserialize, Serialize};

use crate::catalog::{Issue, Problem, ProblemFiles, Track};
use crate::model::{Band, Language, Mode, ProblemFile, Section, StageDef, Status, Tier};

/// Whether a problem introduces its technique or practises one introduced elsewhere.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Role {
    MustLearn,
    Practice,
}

/// A company that asks a problem, from the public company lists.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Company {
    pub name: String,
    /// One of [`DsaCatalog::company_groups`].
    pub group: String,
    /// How often it's asked, 0–100, relative to the company's other problems.
    pub frequency: f32,
    /// Asked in the last six months.
    pub recent: bool,
}

/// The written lesson for a problem (`content/dsa/pages/<slug>.toml`): the intuition, tips, and Python solutions that
/// paste into LeetCode. Text is markdown. `tools/neetcode/check_pages.py` checks the code.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Page {
    pub intuition: String,
    pub tips: Vec<String>,
    pub approaches: Vec<Approach>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Approach {
    pub name: String,
    /// A two-word tag for the tab, e.g. "hash map".
    pub label: String,
    pub idea: String,
    pub code: String,
    pub time: String,
    pub space: String,
    pub note: String,
}

/// What a DSA problem has beyond a Rust one.
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct DsaProblem {
    pub slug: String,
    /// LeetCode's number.
    pub number: u32,
    /// `blind75`, `neetcode150`, `neetcode250`, `all`: the lists it's in, narrowest first.
    pub lists: Vec<String>,
    /// Needs LeetCode Premium.
    pub premium: bool,
    pub companies: Vec<Company>,
    /// NeetCode's video, if there is one.
    pub video: Option<String>,
    /// The technique it belongs to, e.g. `Graphs:topo`.
    pub technique: String,
    pub role: Role,
    /// For a practice problem, the must-learn problem that teaches its technique.
    pub practice_of: Option<String>,
    /// The written lesson, when there is one. Served by its own endpoint, not with the lists.
    #[serde(skip)]
    pub page: Option<Page>,
}

/// One idea a pattern lesson teaches.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Technique {
    pub id: String,
    pub pattern: String,
    pub name: String,
    /// The problem id that teaches it first.
    pub must_learn: String,
    pub problems: u32,
}

/// A group of companies the filters offer together, e.g. Big Tech.
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct CompanyGroup {
    pub name: String,
    pub companies: Vec<String>,
}

#[derive(Debug, Clone, Default)]
pub struct DsaCatalog {
    pub techniques: Vec<Technique>,
    /// In display order.
    pub company_groups: Vec<CompanyGroup>,
    /// The pattern lessons, by technique id (`content/dsa/lessons/<pattern>.toml`).
    pub lessons: BTreeMap<String, Lesson>,
    /// A sentence or two introducing each pattern's lessons, by pattern name.
    pub lesson_intros: BTreeMap<String, String>,
}

/// What a pattern lesson says about one technique: when to reach for it, a Python template to adapt, and the usual traps.
/// `tools/neetcode/check_lessons.py` runs the template.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Lesson {
    /// The technique id, e.g. `Graphs:topo`.
    pub id: String,
    /// The signals in a problem that call for it.
    pub signals: Vec<String>,
    pub template: String,
    pub pitfalls: Vec<String>,
}

/// `<root>/dsa/lessons/<pattern>.toml`: the lessons of one pattern.
#[derive(Deserialize)]
#[serde(deny_unknown_fields)]
struct LessonFile {
    /// The pattern's name, as in `problems.json`.
    pattern: String,
    intro: String,
    technique: Vec<Lesson>,
}

#[derive(Deserialize)]
struct File {
    #[serde(default, deserialize_with = "ordered_groups")]
    company_groups: Vec<CompanyGroup>,
    techniques: Vec<Technique>,
    problems: Vec<Raw>,
}

#[derive(Deserialize)]
struct Raw {
    id: String,
    slug: String,
    number: u32,
    title: String,
    difficulty: Band,
    pattern: String,
    lists: Vec<String>,
    premium: bool,
    tags: Vec<String>,
    companies: Vec<Company>,
    #[serde(default)]
    video: Option<String>,
    technique: String,
    order: u32,
    role: Role,
    #[serde(default)]
    practice_of: Option<String>,
}

/// A JSON object read as a list, keeping the file's order (a map would sort the keys).
fn ordered_groups<'de, D: serde::Deserializer<'de>>(d: D) -> Result<Vec<CompanyGroup>, D::Error> {
    struct Groups;
    impl<'de> serde::de::Visitor<'de> for Groups {
        type Value = Vec<CompanyGroup>;
        fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
            f.write_str("an object of company groups")
        }
        fn visit_map<A: serde::de::MapAccess<'de>>(self, mut map: A) -> Result<Self::Value, A::Error> {
            let mut groups = Vec::new();
            while let Some((name, companies)) = map.next_entry::<String, Vec<String>>()? {
                groups.push(CompanyGroup { name, companies });
            }
            Ok(groups)
        }
    }
    d.deserialize_map(Groups)
}

/// What `load` produces: the pattern tracks (the NeetCode lists), the same patterns holding only their practice
/// problems, and the lists around them.
pub(crate) struct Loaded {
    pub tracks: Vec<Track>,
    pub practice_tracks: Vec<Track>,
    pub catalog: DsaCatalog,
}

impl Loaded {
    fn empty() -> Self {
        Loaded { tracks: Vec::new(), practice_tracks: Vec::new(), catalog: DsaCatalog::default() }
    }
}

#[derive(Deserialize)]
struct PracticeFile {
    problems: Vec<Raw>,
}

/// Reads `<root>/dsa/problems.json` and `practice.json`. Absent means no DSA section; a broken file is reported, not fatal.
pub(crate) fn load(root: &Path, issues: &mut Vec<Issue>) -> Loaded {
    let path = root.join("dsa").join("problems.json");
    let Ok(text) = std::fs::read_to_string(&path) else {
        return Loaded::empty();
    };
    let file: File = match serde_json::from_str(&text) {
        Ok(f) => f,
        Err(e) => {
            issues.push(Issue { path, message: format!("invalid JSON: {e}") });
            return Loaded::empty();
        }
    };
    let by_id: BTreeMap<&str, &Raw> = file.problems.iter().map(|p| (p.id.as_str(), p)).collect();
    for t in &file.techniques {
        match by_id.get(t.must_learn.as_str()) {
            Some(p) if p.role == Role::MustLearn && p.technique == t.id => {}
            _ => issues.push(Issue { path: path.clone(), message: format!("technique {}: {} isn't its must-learn problem", t.id, t.must_learn) }),
        }
    }
    for p in &file.problems {
        if let Some(teacher) = &p.practice_of
            && by_id.get(teacher.as_str()).is_none_or(|t| t.role != Role::MustLearn)
        {
            issues.push(Issue { path: path.clone(), message: format!("{}: practice_of {teacher} isn't a must-learn problem", p.id) });
        }
    }

    // One track per pattern, in NeetCode's order.
    let mut patterns: Vec<(&str, u32)> = Vec::new();
    for p in &file.problems {
        match patterns.iter_mut().find(|(name, _)| *name == p.pattern) {
            Some((_, first)) => *first = (*first).min(p.order),
            None => patterns.push((&p.pattern, p.order)),
        }
    }
    patterns.sort_by_key(|&(_, first)| first);
    let pages = load_pages(root, &by_id, issues);
    let names: BTreeMap<&str, &str> = file.techniques.iter().map(|t| (t.id.as_str(), t.name.as_str())).collect();

    let tracks: Vec<Track> = patterns
        .iter()
        .enumerate()
        .map(|(i, (pattern, _))| {
            let number = i + 1;
            let mut problems: Vec<Problem> = file
                .problems
                .iter()
                .filter(|p| p.pattern == *pattern)
                .map(|p| problem(p, &names, root, pages.get(p.slug.as_str())))
                .collect();
            problems.sort_by_key(|p| p.meta.order);
            Track {
                slug: format!("d{number}-{}", slugify(pattern)),
                code: format!("D{number}"),
                name: (*pattern).to_owned(),
                section: Section::Dsa,
                tier: Tier::Core,
                order: number as u32,
                summary: String::new(),
                pattern: None,
                stages: [Band::Easy, Band::Medium, Band::Hard]
                    .into_iter()
                    .map(|band| StageDef { slug: band_name(band).into(), name: capitalized(band_name(band)), band })
                    .collect(),
                problems,
            }
        })
        .collect();
    let practice_tracks = load_practice(root, &file, &tracks, &names, issues);
    let (lessons, lesson_intros) = load_lessons(root, &file.techniques, issues);
    Loaded { tracks, practice_tracks, catalog: DsaCatalog { techniques: file.techniques, company_groups: file.company_groups, lessons, lesson_intros } }
}

/// `<root>/dsa/practice.json`: LeetCode problems **outside** the NeetCode lists that drill a technique (decision 24).
/// They load as problems in a hidden copy of each pattern's track, so they can be logged and show in activity, but never
/// count toward the lists, a track's readiness or the review schedule.
fn load_practice(root: &Path, main: &File, tracks: &[Track], names: &BTreeMap<&str, &str>, issues: &mut Vec<Issue>) -> Vec<Track> {
    let path = root.join("dsa").join("practice.json");
    let Ok(text) = std::fs::read_to_string(&path) else {
        return Vec::new();
    };
    let file: PracticeFile = match serde_json::from_str(&text) {
        Ok(f) => f,
        Err(e) => {
            issues.push(Issue { path, message: format!("invalid JSON: {e}") });
            return Vec::new();
        }
    };
    let known: std::collections::HashSet<&str> = main.problems.iter().map(|p| p.id.as_str()).collect();
    let techniques: BTreeMap<&str, &Technique> = main.techniques.iter().map(|t| (t.id.as_str(), t)).collect();
    let mut seen = std::collections::HashSet::new();
    let mut by_pattern: BTreeMap<&str, Vec<Problem>> = BTreeMap::new();
    for p in &file.problems {
        let problem_issue = |message: String| Issue { path: path.clone(), message: format!("{}: {message}", p.id) };
        if known.contains(p.id.as_str()) {
            issues.push(problem_issue("is already in the NeetCode lists".into()));
        } else if !seen.insert(p.id.as_str()) {
            issues.push(problem_issue("is listed twice".into()));
        } else if p.premium {
            issues.push(problem_issue("needs LeetCode Premium; practice problems are free ones".into()));
        } else if !techniques.contains_key(p.technique.as_str()) {
            issues.push(problem_issue(format!("unknown technique {}", p.technique)));
        } else if techniques[p.technique.as_str()].pattern != p.pattern {
            issues.push(problem_issue(format!("technique {} belongs to {}, not {}", p.technique, techniques[p.technique.as_str()].pattern, p.pattern)));
        } else if !tracks.iter().any(|t| t.name == p.pattern) {
            issues.push(problem_issue(format!("unknown pattern {}", p.pattern)));
        } else {
            by_pattern.entry(p.pattern.as_str()).or_default().push(problem(p, names, root, None));
        }
    }
    tracks
        .iter()
        .filter_map(|t| {
            let mut problems = by_pattern.remove(t.name.as_str())?;
            problems.sort_by_key(|p| p.meta.order);
            Some(Track {
                slug: t.slug.clone(),
                code: t.code.clone(),
                name: t.name.clone(),
                section: Section::Dsa,
                tier: t.tier,
                order: t.order,
                summary: String::new(),
                pattern: None,
                stages: t.stages.clone(),
                problems,
            })
        })
        .collect()
}

fn problem(p: &Raw, names: &BTreeMap<&str, &str>, root: &Path, page: Option<&Page>) -> Problem {
    Problem {
        id: p.id.clone(),
        meta: ProblemFile {
            slug: p.slug.clone(),
            title: p.title.clone(),
            mode: Mode::Write,
            language: Language::Python,
            unlocked_by: Vec::new(),
            warmup: false,
            level: p.difficulty,
            stage: band_name(p.difficulty).into(),
            order: p.order,
            status: Status::Ready,
            tags: p.tags.clone(),
            companies: p.companies.iter().map(|c| c.name.clone()).collect(),
            teaches: names.get(p.technique.as_str()).map(|n| vec![(*n).to_owned()]).unwrap_or_default(),
            constraints: Vec::new(),
            examples: Vec::new(),
            hints: Vec::new(),
            follow_up: None,
            related: Vec::new(),
            solution: None,
            rules: None,
            source: None,
            renamed_from: Vec::new(),
            crates: Vec::new(),
            perf: None,
        },
        dir: root.join("dsa"),
        files: ProblemFiles::default(),
        dsa: Some(DsaProblem {
            slug: p.slug.clone(),
            number: p.number,
            lists: p.lists.clone(),
            premium: p.premium,
            companies: p.companies.clone(),
            video: p.video.clone(),
            technique: p.technique.clone(),
            role: p.role,
            practice_of: p.practice_of.clone(),
            page: page.cloned(),
        }),
    }
}

/// `<root>/dsa/lessons/*.toml`: the pattern lessons. A lesson for an unknown technique, one filed under the wrong pattern,
/// a duplicate or an empty one is reported. Techniques without a lesson are allowed (the page says so).
fn load_lessons(root: &Path, techniques: &[Technique], issues: &mut Vec<Issue>) -> (BTreeMap<String, Lesson>, BTreeMap<String, String>) {
    let dir = root.join("dsa").join("lessons");
    let mut lessons = BTreeMap::new();
    let mut intros = BTreeMap::new();
    let Ok(entries) = std::fs::read_dir(&dir) else { return (lessons, intros) };
    let mut files: Vec<_> = entries.filter_map(|e| e.ok()).map(|e| e.path()).filter(|p| p.extension().is_some_and(|x| x == "toml")).collect();
    files.sort();
    for path in files {
        let file: LessonFile = match std::fs::read_to_string(&path).map_err(|e| e.to_string()).and_then(|t| toml::from_str(&t).map_err(|e| e.message().to_owned())) {
            Ok(f) => f,
            Err(message) => {
                issues.push(Issue { path, message });
                continue;
            }
        };
        if !techniques.iter().any(|t| t.pattern == file.pattern) {
            issues.push(Issue { path, message: format!("unknown pattern {}", file.pattern) });
            continue;
        }
        if file.intro.trim().is_empty() {
            issues.push(Issue { path: path.clone(), message: "the intro is empty".into() });
        }
        intros.insert(file.pattern.clone(), file.intro);
        for lesson in file.technique {
            let problem = |message: String| Issue { path: path.clone(), message: format!("{}: {message}", lesson.id) };
            match techniques.iter().find(|t| t.id == lesson.id) {
                None => issues.push(problem("isn't a technique".into())),
                Some(t) if t.pattern != file.pattern => issues.push(problem(format!("belongs to {}, not {}", t.pattern, file.pattern))),
                Some(_) if lessons.contains_key(&lesson.id) => issues.push(problem("has two lessons".into())),
                Some(_) if lesson.signals.is_empty() || lesson.pitfalls.is_empty() || lesson.template.trim().is_empty() => {
                    issues.push(problem("needs signals, a template and pitfalls".into()));
                }
                Some(_) => {
                    lessons.insert(lesson.id.clone(), lesson);
                }
            }
        }
    }
    (lessons, intros)
}

/// `<root>/dsa/pages/<slug>.toml`, by slug. A page for a problem that isn't in the lists is reported.
fn load_pages(root: &Path, by_id: &BTreeMap<&str, &Raw>, issues: &mut Vec<Issue>) -> BTreeMap<String, Page> {
    let dir = root.join("dsa").join("pages");
    let mut pages = BTreeMap::new();
    let Ok(entries) = std::fs::read_dir(&dir) else { return pages };
    let mut files: Vec<_> = entries.filter_map(|e| e.ok()).map(|e| e.path()).filter(|p| p.extension().is_some_and(|x| x == "toml")).collect();
    files.sort();
    for path in files {
        let slug = path.file_stem().map(|s| s.to_string_lossy().into_owned()).unwrap_or_default();
        if !by_id.contains_key(format!("lc-{slug}").as_str()) {
            issues.push(Issue { path, message: format!("{slug} isn't a problem in the NeetCode lists") });
            continue;
        }
        match std::fs::read_to_string(&path).map_err(|e| e.to_string()).and_then(|t| toml::from_str::<Page>(&t).map_err(|e| e.message().to_owned())) {
            Ok(page) if page.approaches.is_empty() => issues.push(Issue { path, message: "a page needs at least one approach".into() }),
            Ok(page) => {
                pages.insert(slug, page);
            }
            Err(message) => issues.push(Issue { path, message }),
        }
    }
    pages
}

fn band_name(band: Band) -> &'static str {
    match band {
        Band::Easy => "easy",
        Band::Medium => "medium",
        Band::Hard => "hard",
    }
}

fn capitalized(word: &str) -> String {
    let mut chars = word.chars();
    chars.next().map(|c| c.to_uppercase().chain(chars).collect()).unwrap_or_default()
}

/// `Heap / Priority Queue` becomes `heap-priority-queue`.
fn slugify(name: &str) -> String {
    let mut out = String::new();
    for c in name.chars() {
        if c.is_ascii_alphanumeric() {
            out.push(c.to_ascii_lowercase());
        } else if !out.ends_with('-') && !out.is_empty() {
            out.push('-');
        }
    }
    out.trim_end_matches('-').to_owned()
}

#[cfg(test)]
mod tests {
    use super::slugify;

    #[test]
    fn slugs_are_folder_safe() {
        assert_eq!(slugify("Heap / Priority Queue"), "heap-priority-queue");
        assert_eq!(slugify("1-D Dynamic Programming"), "1-d-dynamic-programming");
        assert_eq!(slugify("Math & Geometry"), "math-geometry");
        assert_eq!(slugify("Arrays & Hashing"), "arrays-hashing");
    }
}
