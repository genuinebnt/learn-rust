//! The on-disk content format: one folder per track, one folder per problem.
//!
//! ```text
//! content/tracks/d9-graphs/
//!   track.toml
//!   problems/network-delay-time/
//!     problem.toml   metadata, hints, rules
//!     statement.md
//!     starter.rs     becomes src/lib.rs in the user's workspace
//!     solution.rs
//!     tests/visible.rs
//!     tests/hidden.rs
//! ```

use serde::{Deserialize, Serialize};

/// Difficulty band. Stages in a track must run Easy → Medium → Hard.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Band {
    Easy,
    Medium,
    Hard,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Section {
    #[serde(rename = "D")]
    Dsa,
    #[serde(rename = "L")]
    Language,
    #[serde(rename = "S")]
    StandardLibrary,
    #[serde(rename = "C")]
    Concurrency,
    #[serde(rename = "Y")]
    Systems,
    #[serde(rename = "B")]
    Backend,
    #[serde(rename = "M")]
    Design,
}

impl Section {
    pub fn letter(self) -> char {
        match self {
            Section::Dsa => 'D',
            Section::Language => 'L',
            Section::StandardLibrary => 'S',
            Section::Concurrency => 'C',
            Section::Systems => 'Y',
            Section::Backend => 'B',
            Section::Design => 'M',
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Tier {
    Core,
    Light,
    Sde3,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Mode {
    /// Signature + tests; the user writes the implementation.
    Write,
    /// A broken program to fix under rules.
    Fix,
    /// One stage of a multi-stage project; only tests are given.
    Stage,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Status {
    Draft,
    Ready,
}

/// `track.toml`
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct TrackFile {
    pub code: String,
    pub name: String,
    pub section: Section,
    pub tier: Tier,
    /// Position in the section's recommended order.
    pub order: u32,
    #[serde(default)]
    pub summary: String,
    pub stages: Vec<StageDef>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct StageDef {
    pub slug: String,
    pub name: String,
    pub band: Band,
}

/// `problem.toml`
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ProblemFile {
    pub slug: String,
    pub title: String,
    pub mode: Mode,
    pub level: Band,
    pub stage: String,
    /// Position within the track; unique per track.
    pub order: u32,
    pub status: Status,
    #[serde(default)]
    pub tags: Vec<String>,
    #[serde(default)]
    pub teaches: Vec<String>,
    #[serde(default)]
    pub constraints: Vec<String>,
    #[serde(default)]
    pub examples: Vec<Example>,
    #[serde(default)]
    pub hints: Vec<Hint>,
    #[serde(default)]
    pub follow_up: Option<String>,
    /// Track codes this problem links to, e.g. `["S5", "S1"]`.
    #[serde(default)]
    pub related: Vec<String>,
    #[serde(default)]
    pub solution: Option<SolutionNotes>,
    #[serde(default)]
    pub rules: Option<Rules>,
    /// Where the problem came from in the old study packet, e.g. `"W42"`.
    #[serde(default)]
    pub source: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Example {
    pub input: String,
    pub output: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Hint {
    pub kind: String,
    pub text: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct SolutionNotes {
    pub explanation: String,
    pub time: String,
    pub space: String,
}

/// Constraints a fix-this attempt must respect, checked before the code runs.
#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Rules {
    /// Method names that may not be called, e.g. `["clone"]`.
    #[serde(default)]
    pub forbid_methods: Vec<String>,
    /// Type names that may not appear, e.g. `["RefCell", "Cell"]`.
    #[serde(default)]
    pub forbid_types: Vec<String>,
    #[serde(default)]
    pub forbid_unsafe: bool,
    /// Most lines that may differ from the starter.
    #[serde(default)]
    pub max_changed_lines: Option<u32>,
}
