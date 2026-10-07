//! The NeetCode lists as DSA tracks, loaded from `content/dsa/problems.json` (built by `tools/neetcode/build.py`).
//!
//! These problems aren't run in anneal: you solve them on LeetCode and log how it went. They load as ordinary tracks
//! (one per NeetCode pattern, ids `lc-<leetcode slug>`) so that streaks, reviews, readiness and the Progress pages
//! treat them like any other problem. [`Problem::dsa`](crate::Problem::dsa) carries what only they have.

use std::collections::BTreeMap;
use std::path::Path;

use serde::{Deserialize, Serialize};

use crate::catalog::{Issue, Problem, ProblemFiles, Track};
use crate::model::{Band, Mode, ProblemFile, Section, StageDef, Status, Tier};

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
    video: Option<String>,
    technique: String,
    order: u32,
    role: Role,
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

/// Reads `<root>/dsa/problems.json`. Absent means no DSA section; a broken file is reported, not fatal.
pub(crate) fn load(root: &Path, issues: &mut Vec<Issue>) -> (Vec<Track>, DsaCatalog) {
    let path = root.join("dsa").join("problems.json");
    let Ok(text) = std::fs::read_to_string(&path) else {
        return (Vec::new(), DsaCatalog::default());
    };
    let file: File = match serde_json::from_str(&text) {
        Ok(f) => f,
        Err(e) => {
            issues.push(Issue { path, message: format!("invalid JSON: {e}") });
            return (Vec::new(), DsaCatalog::default());
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

    let tracks = patterns
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
                stages: [Band::Easy, Band::Medium, Band::Hard]
                    .into_iter()
                    .map(|band| StageDef { slug: band_name(band).into(), name: capitalized(band_name(band)), band })
                    .collect(),
                problems,
            }
        })
        .collect();
    (tracks, DsaCatalog { techniques: file.techniques, company_groups: file.company_groups })
}

fn problem(p: &Raw, names: &BTreeMap<&str, &str>, root: &Path, page: Option<&Page>) -> Problem {
    Problem {
        id: p.id.clone(),
        meta: ProblemFile {
            slug: p.slug.clone(),
            title: p.title.clone(),
            mode: Mode::Write,
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
