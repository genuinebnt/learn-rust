//! Progressive reveal: a learner's repo shows only the modules they have reached.
//!
//! Every template file belongs to the *first module that has a stage in it* (found from the `@begin` markers of the reference when
//! the template is generated) and is listed in `template/.anneal-files.json`. Files with no stage in them, and `lib.rs`, are always
//! there. A `mod.rs` is there as soon as something under it is, and its `pub mod x;` lines are dropped for files that are not there,
//! so the repo compiles with only the modules unlocked so far. Passing the last stage of a module unlocks the next one.
//!
//! A module's `module.toml` may list `files = [...]` that must arrive with it even though a later module's stage also touches them
//! (the page guards a buffer pool already names, say); `anneal course verify` compiles every unlock state, so a missing one shows up.

use std::collections::{BTreeMap, BTreeSet, HashMap};
use std::fs;
use std::path::{Path, PathBuf};

use anyhow::Context;

/// Where the file → module map lives, inside the template.
pub const FILES_JSON: &str = ".anneal-files.json";

fn key(p: &Path) -> String {
    p.components().map(|c| c.as_os_str().to_string_lossy().into_owned()).collect::<Vec<_>>().join("/")
}

/// File → first module that touches it. `stage_module`: stage id → module code; `order`: module codes in course order;
/// `module_files`: each module's `files` overrides; `boss_bins`: test binary → module of the boss stage that runs it.
pub fn file_modules(
    reference: &Path,
    order: &[String],
    stage_module: &HashMap<String, String>,
    module_files: &BTreeMap<String, Vec<String>>,
    boss_bins: &HashMap<String, String>,
) -> anyhow::Result<BTreeMap<String, String>> {
    let pos = |m: &str| order.iter().position(|x| x == m).unwrap_or(usize::MAX);
    let mut map: BTreeMap<String, String> = BTreeMap::new();
    let mut put = |rel: String, module: &str| {
        let better = map.get(&rel).is_none_or(|old| pos(module) < pos(old));
        if better {
            map.insert(rel, module.to_owned());
        }
    };
    fn walk(base: &Path, dir: &Path, out: &mut Vec<PathBuf>) -> anyhow::Result<()> {
        let mut es: Vec<_> = fs::read_dir(dir)?.filter_map(|e| e.ok()).collect();
        es.sort_by_key(|e| e.file_name());
        for e in es {
            let p = e.path();
            let name = e.file_name().to_string_lossy().into_owned();
            if matches!(name.as_str(), "target" | ".git" | ".DS_Store") {
                continue;
            }
            if p.is_dir() {
                walk(base, &p, out)?;
            } else {
                out.push(p.strip_prefix(base)?.to_path_buf());
            }
        }
        Ok(())
    }
    let mut files = Vec::new();
    walk(reference, reference, &mut files)?;
    for rel in files {
        let k = key(&rel);
        let text = fs::read_to_string(reference.join(&rel)).unwrap_or_default();
        if k.starts_with("src/") && k.ends_with(".rs") {
            for line in text.lines() {
                if let Some(id) = line.trim_start().strip_prefix("//").map(str::trim_start).and_then(|r| r.strip_prefix("@begin ")) {
                    let id = id.trim();
                    let module = stage_module.get(id).with_context(|| format!("{k}: unknown stage {id:?}"))?;
                    put(k.clone(), module);
                }
            }
        } else if let Some(code) = k.strip_prefix("tests/stages_").and_then(|r| r.strip_suffix(".rs")) {
            put(k.clone(), code);
        } else if let Some(bin) = k.strip_prefix("tests/").and_then(|r| r.strip_suffix(".rs"))
            && !bin.contains('/')
            && let Some(m) = boss_bins.get(bin)
        {
            put(k.clone(), m);
        }
    }
    for (module, list) in module_files {
        for f in list {
            put(f.clone(), module);
        }
    }
    Ok(map)
}

/// Is this file only `mod x;` lines (and comments)? Such a file belongs to whatever it declares; any other mod.rs has code of its own
/// (a test helper, say) and is always there.
pub fn only_declares(text: &str) -> bool {
    text.lines().map(str::trim).filter(|l| !l.is_empty() && !l.starts_with("//") && !l.starts_with("#!")).all(|l| {
        (l.starts_with("pub mod ") || l.starts_with("mod ") || l.starts_with("pub(crate) mod ")) && l.ends_with(';')
    })
}

/// The template files a learner who has unlocked `unlocked` can see. `declares_only(f)` says whether a mod.rs is only declarations.
pub fn visible(files: &[PathBuf], map: &BTreeMap<String, String>, unlocked: &[String], declares_only: &dyn Fn(&Path) -> bool) -> BTreeSet<PathBuf> {
    let mut vis: BTreeSet<PathBuf> = BTreeSet::new();
    let mut mods: Vec<&PathBuf> = Vec::new();
    for f in files {
        let k = key(f);
        if k == FILES_JSON {
            continue;
        }
        if f.file_name().is_some_and(|n| n == "mod.rs") && declares_only(f) {
            mods.push(f);
        } else if map.get(&k).is_none_or(|m| unlocked.contains(m)) {
            vis.insert(f.clone());
        }
    }
    // A mod.rs is there once anything under its directory is; deepest first, so a directory of directories works.
    mods.sort_by_key(|p| std::cmp::Reverse(p.components().count()));
    for m in mods {
        let dir = m.parent().unwrap_or(Path::new(""));
        if vis.iter().any(|v| v.starts_with(dir) && v != m) {
            vis.insert(m.clone());
        }
    }
    vis
}

/// `text` of a mod.rs or lib.rs without the `pub mod x;` lines whose target isn't visible.
pub fn filter_mod(text: &str, dir: &Path, vis: &BTreeSet<PathBuf>) -> String {
    let mut out = String::with_capacity(text.len());
    for line in text.split_inclusive('\n') {
        let t = line.trim();
        let name = t.strip_prefix("pub mod ").or_else(|| t.strip_prefix("mod ")).and_then(|r| r.strip_suffix(';')).map(str::trim);
        if let Some(n) = name {
            let here = dir.join(format!("{n}.rs"));
            let nested = dir.join(n).join("mod.rs");
            if !vis.contains(&here) && !vis.contains(&nested) {
                continue;
            }
        }
        out.push_str(line);
    }
    out
}

/// Is this file filtered rather than copied as is?
pub fn is_module_file(rel: &Path) -> bool {
    rel.file_name().is_some_and(|n| n == "mod.rs") || key(rel) == "src/lib.rs"
}

#[cfg(test)]
mod tests {
    use super::*;

    fn p(s: &str) -> PathBuf {
        PathBuf::from(s)
    }

    #[test]
    fn a_mod_rs_with_code_is_not_only_declarations() {
        assert!(only_declares("pub mod a;\n// note\nmod b;\n"));
        assert!(!only_declares("pub fn helper() {}\n"));
        assert!(!only_declares("pub mod a;\npub fn helper() {}\n"));
    }

    #[test]
    fn a_mod_rs_appears_with_its_first_file_and_loses_hidden_lines() {
        let files = vec![p("src/lib.rs"), p("src/a/mod.rs"), p("src/a/x.rs"), p("src/a/y.rs"), p("src/b/mod.rs"), p("src/b/z.rs"), p("src/given.rs")];
        let map: BTreeMap<String, String> = [("src/a/x.rs", "1a"), ("src/a/y.rs", "1b"), ("src/b/z.rs", "1b")].into_iter().map(|(a, b)| (a.to_owned(), b.to_owned())).collect();
        let vis = visible(&files, &map, &["1a".to_owned()], &|_| true);
        assert!(vis.contains(&p("src/a/mod.rs")) && vis.contains(&p("src/a/x.rs")) && vis.contains(&p("src/given.rs")));
        assert!(!vis.contains(&p("src/a/y.rs")) && !vis.contains(&p("src/b/mod.rs")) && !vis.contains(&p("src/b/z.rs")));
        assert_eq!(filter_mod("pub mod x;\npub mod y;\n", Path::new("src/a"), &vis), "pub mod x;\n");
        assert_eq!(filter_mod("pub mod a;\npub mod b;\n", Path::new("src"), &vis), "pub mod a;\n");
        let all = visible(&files, &map, &["1a".to_owned(), "1b".to_owned()], &|_| true);
        assert_eq!(filter_mod("pub mod a;\npub mod b;\n", Path::new("src"), &all), "pub mod a;\npub mod b;\n");
    }
}
