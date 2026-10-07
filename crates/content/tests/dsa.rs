//! The DSA section: `dsa/problems.json` loads as tracks, and the checks around it.

use std::path::Path;

use anneal_content::{Catalog, Role, Section};

fn fixture() -> std::path::PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("fixtures/dsa-root")
}

/// A content root holding a copy of the fixture's `dsa/problems.json` and an empty `tracks/`.
fn root_with(problems_json: &str) -> tempfile::TempDir {
    let dir = tempfile::tempdir().unwrap();
    std::fs::create_dir_all(dir.path().join("tracks")).unwrap();
    std::fs::create_dir_all(dir.path().join("dsa")).unwrap();
    std::fs::write(dir.path().join("dsa/problems.json"), problems_json).unwrap();
    dir
}

#[test]
fn the_lists_load_as_one_track_per_pattern() {
    let root = root_with(&std::fs::read_to_string(fixture().join("dsa/problems.json")).unwrap());
    let loaded = Catalog::load(root.path()).unwrap();
    assert!(loaded.issues.is_empty(), "{:?}", loaded.issues);
    let c = loaded.catalog;
    let tracks: Vec<_> = c.tracks.iter().map(|t| (t.code.as_str(), t.slug.as_str(), t.section, t.problems.len())).collect();
    assert_eq!(tracks, [("D1", "d1-arrays-hashing", Section::Dsa, 3), ("D2", "d2-two-pointers", Section::Dsa, 3)]);
    // Problems keep NeetCode's order inside a track, and the id is `lc-<slug>`.
    let ids: Vec<_> = c.tracks[0].problems.iter().map(|p| p.id.as_str()).collect();
    assert_eq!(ids, ["lc-contains-duplicate", "lc-two-sum", "lc-encode-and-decode-strings"]);

    let (t, p) = c.problem("lc-two-sum-ii-input-array-is-sorted").unwrap();
    let dsa = p.dsa.as_ref().unwrap();
    assert_eq!((t.code.as_str(), dsa.number, dsa.role, dsa.practice_of.as_deref()), ("D2", 167, Role::Practice, Some("lc-valid-palindrome")));
    assert_eq!(p.meta.teaches, ["Pointers from both ends"]);
    assert_eq!(p.meta.stage, "medium");
    assert_eq!(t.stages.iter().map(|s| s.slug.as_str()).collect::<Vec<_>>(), ["easy", "medium", "hard"]);
    assert_eq!(c.dsa.techniques.len(), 4);
    assert_eq!((c.dsa.company_groups[0].name.as_str(), c.dsa.company_groups[0].companies.as_slice()), ("Big Tech", ["Google".to_owned(), "Amazon".to_owned()].as_slice()));
    assert!(c.knows("lc-two-sum") && !c.knows("lc-nope"));
}

#[test]
fn a_dsa_section_is_optional() {
    let empty = tempfile::tempdir().unwrap();
    std::fs::create_dir(empty.path().join("tracks")).unwrap();
    let loaded = Catalog::load(empty.path()).unwrap();
    assert!(loaded.issues.is_empty() && loaded.catalog.tracks.is_empty());
}

#[test]
fn inconsistent_technique_data_is_reported() {
    let json = std::fs::read_to_string(fixture().join("dsa/problems.json")).unwrap();
    // A practice problem pointing at another practice problem, and a technique naming the wrong must-learn.
    let broken = json
        .replace(r#""practice_of": "lc-valid-palindrome"}"#, r#""practice_of": "lc-reverse-string"}"#)
        .replace(r#""must_learn": "lc-two-sum""#, r#""must_learn": "lc-valid-palindrome""#);
    let dir = root_with(&broken);
    let issues: Vec<String> = Catalog::load(dir.path()).unwrap().issues.into_iter().map(|i| i.message).collect();
    assert!(issues.iter().any(|m| m.contains("practice_of lc-reverse-string isn't a must-learn")), "{issues:?}");
    assert!(issues.iter().any(|m| m.contains("technique Arrays & Hashing:complement")), "{issues:?}");

    std::fs::write(dir.path().join("dsa/problems.json"), "{ not json").unwrap();
    let issues = Catalog::load(dir.path()).unwrap().issues;
    assert!(issues.len() == 1 && issues[0].message.starts_with("invalid JSON"), "{issues:?}");
}

#[test]
fn retired_ids_are_known_but_cannot_be_current() {
    let dir = tempfile::tempdir().unwrap();
    std::fs::create_dir_all(dir.path().join("tracks")).unwrap();
    std::fs::write(dir.path().join("retired.txt"), "# why\nd1-old\n\n  d2-older   # trailing note\n").unwrap();
    let c = Catalog::load(dir.path()).unwrap().catalog;
    assert!(c.knows("d1-old") && c.knows("d2-older") && !c.knows("d3-new"));
    assert_eq!(c.retired.len(), 2);
}

#[test]
fn pages_must_belong_to_a_listed_problem_and_parse() {
    let dir = root_with(&std::fs::read_to_string(fixture().join("dsa/problems.json")).unwrap());
    std::fs::create_dir_all(dir.path().join("dsa/pages")).unwrap();
    std::fs::write(dir.path().join("dsa/pages/not-a-problem.toml"), "intuition = \"x\"\n").unwrap();
    std::fs::write(dir.path().join("dsa/pages/two-sum.toml"), "intuition = \"x\"\n").unwrap(); // no tips, no approaches
    let issues: Vec<String> = Catalog::load(dir.path()).unwrap().issues.into_iter().map(|i| i.message).collect();
    assert!(issues.iter().any(|m| m.contains("not-a-problem isn't a problem in the NeetCode lists")), "{issues:?}");
    assert!(issues.iter().any(|m| m.contains("missing field")), "{issues:?}");

    std::fs::copy(fixture().join("dsa/pages/two-sum.toml"), dir.path().join("dsa/pages/two-sum.toml")).unwrap();
    std::fs::remove_file(dir.path().join("dsa/pages/not-a-problem.toml")).unwrap();
    let loaded = Catalog::load(dir.path()).unwrap();
    assert!(loaded.issues.is_empty(), "{:?}", loaded.issues);
    let (_, p) = loaded.catalog.problem("lc-two-sum").unwrap();
    assert_eq!(p.dsa.as_ref().unwrap().page.as_ref().unwrap().approaches.len(), 1);
}

#[test]
fn lessons_belong_to_a_technique_of_their_pattern_and_are_complete() {
    let dir = root_with(&std::fs::read_to_string(fixture().join("dsa/problems.json")).unwrap());
    std::fs::create_dir_all(dir.path().join("dsa/lessons")).unwrap();
    let good = std::fs::read_to_string(fixture().join("dsa/lessons/two-pointers.toml")).unwrap();
    let write = |name: &str, text: &str| std::fs::write(dir.path().join("dsa/lessons").join(name), text).unwrap();
    let issues = |dir: &std::path::Path| -> Vec<String> { Catalog::load(dir).unwrap().issues.into_iter().map(|i| i.message).collect() };

    write("two-pointers.toml", &good);
    let loaded = Catalog::load(dir.path()).unwrap();
    assert!(loaded.issues.is_empty(), "{:?}", loaded.issues);
    assert_eq!(loaded.catalog.dsa.lessons["Two Pointers:opposite"].signals.len(), 2);
    assert!(loaded.catalog.dsa.lesson_intros["Two Pointers"].starts_with("Two indexes"));

    // The same technique filed under another pattern, one that doesn't exist, a duplicate and an empty lesson.
    write("wrong-pattern.toml", &good.replace("pattern = \"Two Pointers\"", "pattern = \"Arrays & Hashing\""));
    write("no-pattern.toml", &good.replace("pattern = \"Two Pointers\"", "pattern = \"Cooking\""));
    write("empty.toml", "pattern = \"Arrays & Hashing\"\nintro = \"x\"\n[[technique]]\nid = \"Arrays & Hashing:seen-set\"\nsignals = []\ntemplate = \"\"\npitfalls = []\n");
    let found = issues(dir.path());
    assert!(found.iter().any(|m| m.contains("Two Pointers:opposite: belongs to Two Pointers, not Arrays & Hashing")), "{found:?}");
    assert!(found.iter().any(|m| m.contains("unknown pattern Cooking")), "{found:?}");
    assert!(found.iter().any(|m| m.contains("Arrays & Hashing:seen-set: needs signals, a template and pitfalls")), "{found:?}");
    std::fs::remove_file(dir.path().join("dsa/lessons/wrong-pattern.toml")).unwrap();
    write("dup.toml", &good);
    assert!(issues(dir.path()).iter().any(|m| m.contains("has two lessons")));
}
