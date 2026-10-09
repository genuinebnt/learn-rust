//! The source of the tests a stage runs, cut out of the template's test files, so the stage page can show a test's code next to its result.

use std::collections::HashMap;
use std::fs;
use std::path::Path;

/// `stage.tests` entries look like `stages_4b::s4b_03` (the file `tests/stages_4b.rs`, the tests whose names start with `s4b_03`) or
/// `slt_expressions_test` (the whole file). Returns test name -> its source, dedented, with its attributes and doc comment.
pub fn stage_test_sources(template: &Path, entries: &[String]) -> HashMap<String, String> {
    let mut out = HashMap::new();
    for entry in entries {
        let (file, prefix) = match entry.split_once("::") {
            Some((f, p)) => (f, p),
            None => (entry.as_str(), ""),
        };
        let Ok(text) = fs::read_to_string(template.join("tests").join(format!("{file}.rs"))) else { continue };
        for (name, src) in test_functions(&text) {
            if name.starts_with(prefix) {
                out.insert(name, src);
            }
        }
    }
    out
}

/// Every `fn name(..) { .. }` of the text that is preceded by `#[test]` (inside or outside a `proptest!` block), with its leading attributes and
/// doc comments, as (name, source).
pub fn test_functions(text: &str) -> Vec<(String, String)> {
    let lines: Vec<&str> = text.lines().collect();
    let offsets: Vec<usize> = {
        let mut o = Vec::with_capacity(lines.len());
        let mut at = 0;
        for l in &lines {
            o.push(at);
            at += l.len() + 1;
        }
        o
    };
    let mut out = Vec::new();
    let mut i = 0;
    while i < lines.len() {
        let t = lines[i].trim_start();
        let is_fn = t.starts_with("fn ") || t.starts_with("pub fn ");
        if !is_fn {
            i += 1;
            continue;
        }
        // attributes and comments right above
        let mut start = i;
        while start > 0 {
            let p = lines[start - 1].trim_start();
            if p.starts_with("#[") || p.starts_with("///") || p.starts_with("//") {
                start -= 1;
            } else {
                break;
            }
        }
        let has_test = lines[start..i].iter().any(|l| l.trim() == "#[test]");
        let name: String = t.trim_start_matches("pub ").trim_start_matches("fn ").chars().take_while(|c| c.is_alphanumeric() || *c == '_').collect();
        let Some(end) = body_end(text, offsets[i]) else {
            i += 1;
            continue;
        };
        // the end offset is just after the closing brace: the line it is on
        let end_line = offsets.partition_point(|o| *o < end).saturating_sub(1).max(i);
        if has_test && !name.is_empty() {
            let block: Vec<&str> = lines[start..=end_line].to_vec();
            out.push((name, dedent(&block)));
        }
        i = end_line + 1;
    }
    out
}

fn dedent(lines: &[&str]) -> String {
    let indent = lines.iter().filter(|l| !l.trim().is_empty()).map(|l| l.len() - l.trim_start().len()).min().unwrap_or(0);
    lines.iter().map(|l| if l.len() >= indent { &l[indent..] } else { l.trim_start() }).collect::<Vec<_>>().join("\n")
}

/// The offset just after the `}` that closes the first top-level `{` at or after `from` (skipping braces in strings, chars and comments).
fn body_end(text: &str, from: usize) -> Option<usize> {
    let b = text.as_bytes();
    let (mut i, mut depth, mut started) = (from, 0usize, false);
    let mut paren = 0i32;
    while i < b.len() {
        match b[i] {
            b'/' if b.get(i + 1) == Some(&b'/') => {
                while i < b.len() && b[i] != b'\n' {
                    i += 1;
                }
                continue;
            }
            b'/' if b.get(i + 1) == Some(&b'*') => {
                i += 2;
                while i + 1 < b.len() && !(b[i] == b'*' && b[i + 1] == b'/') {
                    i += 1;
                }
                i += 2;
                continue;
            }
            b'r' if matches!(b.get(i + 1), Some(b'"') | Some(b'#')) && (i == 0 || !(b[i - 1].is_ascii_alphanumeric() || b[i - 1] == b'_')) => {
                let mut j = i + 1;
                let mut hashes = 0;
                while b.get(j) == Some(&b'#') {
                    hashes += 1;
                    j += 1;
                }
                if b.get(j) == Some(&b'"') {
                    j += 1;
                    let close: Vec<u8> = std::iter::once(b'"').chain(std::iter::repeat_n(b'#', hashes)).collect();
                    while j < b.len() && !b[j..].starts_with(&close) {
                        j += 1;
                    }
                    i = j + close.len();
                    continue;
                }
            }
            b'"' => {
                i += 1;
                while i < b.len() && b[i] != b'"' {
                    if b[i] == b'\\' {
                        i += 1;
                    }
                    i += 1;
                }
            }
            b'\'' => {
                // a char literal ('x', '\n', '{'), not a lifetime
                if b.get(i + 1) == Some(&b'\\') {
                    if let Some(k) = b[i + 2..].iter().take(10).position(|c| *c == b'\'') {
                        i += k + 3;
                        continue;
                    }
                } else if b.get(i + 2) == Some(&b'\'') {
                    i += 3;
                    continue;
                } else if let Some(c) = text[i + 1..].chars().next().filter(|c| text[i + 1 + c.len_utf8()..].starts_with('\'')) {
                    i += 2 + c.len_utf8();
                    continue;
                }
            }
            b'(' => paren += 1,
            b')' => paren -= 1,
            b'{' if paren <= 0 => {
                depth += 1;
                started = true;
            }
            b'}' if paren <= 0 && started => {
                depth -= 1;
                if depth == 0 {
                    return Some(i + 1);
                }
            }
            b'{' => {}
            b'}' => {}
            _ => {}
        }
        i += 1;
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cuts_plain_and_proptest_tests() {
        let src = r##"
use x;

/// A doc line.
#[test]
fn first_one() {
    let s = "a } b";
    let c = '}';
    assert!(s.len() > 0, "{}", r#"raw } "quoted""#);
}

fn helper() { }

proptest! {
    #![proptest_config(ProptestConfig::default())]

    /// Properties.
    #[test]
    fn second(a in 0..5i32, v in prop::collection::vec(0..3, 0..4)) {
        prop_assert!(a >= 0);
        let _ = |x: u8| { x };
    }
}
"##;
        let found = test_functions(src);
        let names: Vec<&str> = found.iter().map(|(n, _)| n.as_str()).collect();
        assert_eq!(names, vec!["first_one", "second"]);
        assert!(found[0].1.starts_with("/// A doc line.\n#[test]\nfn first_one() {"));
        assert!(found[0].1.ends_with("}"));
        assert!(found[1].1.starts_with("/// Properties.\n#[test]\nfn second(a in"), "{}", found[1].1);
        assert!(found[1].1.trim_end().ends_with("}"));
        assert!(!found[1].1.contains("proptest!"));
    }

    #[test]
    fn selects_by_prefix() {
        let dir = std::env::temp_dir().join(format!("anneal-ts-{}", std::process::id()));
        std::fs::create_dir_all(dir.join("tests")).unwrap();
        std::fs::write(dir.join("tests/stages_x.rs"), "#[test]\nfn s1_a() {}\n#[test]\nfn s2_b() {}\n").unwrap();
        let got = stage_test_sources(&dir, &["stages_x::s1".to_string()]);
        assert_eq!(got.keys().collect::<Vec<_>>(), vec!["s1_a"]);
        let all = stage_test_sources(&dir, &["stages_x".to_string()]);
        assert_eq!(all.len(), 2);
        std::fs::remove_dir_all(&dir).ok();
    }
}

#[cfg(test)]
mod course_tests {
    use super::*;

    /// Every test of every stage of the shipped course has its source cut out whole: it ends with a closing brace and its braces balance.
    #[test]
    fn every_stage_of_the_bustub_course_finds_its_tests() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../courses/bustub");
        let Ok(course) = crate::course::Course::load_all(&root) else { return };
        let mut checked = 0;
        for m in &course.modules {
            for s in &m.stages {
                for (name, src) in &s.test_sources {
                    assert!(src.contains(&format!("fn {name}(")), "{}: {name}", s.id);
                    let (open, close) = (src.matches('{').count(), src.matches('}').count());
                    assert!(src.trim_end().ends_with('}'), "{}: {name} does not end at its closing brace", s.id);
                    assert!(open >= close.saturating_sub(40) && close > 0, "{}: {name}", s.id);
                    checked += 1;
                }
                if s.kind != "boss" && !m.planned {
                    assert!(!s.test_sources.is_empty(), "{} has no test sources", s.id);
                }
            }
        }
        assert!(checked > 100, "only {checked} tests found");
    }
}
