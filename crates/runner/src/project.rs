//! Writes a submission out as a throwaway cargo package named `solution`.

use std::fs;
use std::io;
use std::path::Path;

use crate::{RunnerError, Scratch, Submission, deps};

/// Prepended to line 1 of every test file, so line numbers in compiler
/// diagnostics still match the author's file. Only columns on line 1 shift.
pub(crate) const TEST_PREFIX: &str =
    r#"#[macro_use] #[path = "anneal/prelude.rs"] mod anneal_prelude; "#;

/// `check!(input, got, expected)`: like `assert_eq!`, but on failure it prints one
/// `ANNEAL {json}` line so the UI can show input / expected / got.
const PRELUDE: &str = r#"#[allow(unused_macros)]
macro_rules! check {
    ($input:expr, $got:expr, $expected:expr $(,)?) => {{
        let got = $got;
        let expected = $expected;
        if got != expected {
            println!(
                "ANNEAL {{\"input\":{},\"expected\":{},\"got\":{}}}",
                crate::anneal_prelude::json(&($input).to_string()),
                crate::anneal_prelude::json(&format!("{:?}", expected)),
                crate::anneal_prelude::json(&format!("{:?}", got)),
            );
            panic!("check failed: expected {:?}, got {:?}", expected, got);
        }
    }};
}

#[allow(dead_code)]
pub fn json(s: &str) -> String {
    let mut out = String::with_capacity(s.len() + 2);
    out.push('"');
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}
"#;

/// Writes `sub` into `dir` as a cargo package named `solution`, with the `check!` prelude.
/// `vendored` points cargo at the sandbox image's vendored crates instead of crates.io.
pub fn write(dir: &Path, sub: &Submission<'_>, vendored: bool) -> Result<(), RunnerError> {
    let deps = deps::dependency_lines(sub.crates).map_err(RunnerError::UnknownCrate)?;
    write_files(dir, sub, &deps, vendored).map_err(|e| RunnerError::io("write project", e))
}

fn write_files(dir: &Path, sub: &Submission<'_>, deps: &str, vendored: bool) -> io::Result<()> {
    fs::create_dir_all(dir.join("src"))?;
    fs::create_dir_all(dir.join("tests/anneal"))?;
    fs::write(dir.join("Cargo.toml"), manifest(sub.hidden_tests.is_some(), deps))?;
    write_deps_config(dir, sub.crates, vendored)?;
    fs::write(dir.join("src/lib.rs"), sub.lib_rs)?;
    fs::write(dir.join("tests/anneal/prelude.rs"), PRELUDE)?;
    fs::write(
        dir.join("tests/visible.rs"),
        format!("{TEST_PREFIX}{}", sub.visible_tests),
    )?;
    if let Some(hidden) = sub.hidden_tests {
        fs::write(
            dir.join("tests/hidden.rs"),
            format!("{TEST_PREFIX}{hidden}"),
        )?;
    }
    Ok(())
}

/// Writes a scratch run into `dir`: the user's library plus `src/bin/scratch.rs` with their `main`.
pub(crate) fn write_scratch(dir: &Path, s: &Scratch<'_>, vendored: bool) -> Result<(), RunnerError> {
    let deps = deps::dependency_lines(s.crates).map_err(RunnerError::UnknownCrate)?;
    let files = || -> io::Result<()> {
        fs::create_dir_all(dir.join("src/bin"))?;
        let mut m = manifest_head();
        m.push_str("\n[[bin]]\nname = \"scratch\"\npath = \"src/bin/scratch.rs\"\ntest = false\n");
        if !deps.is_empty() {
            m.push_str("\n[dependencies]\n");
            m.push_str(&deps);
        }
        fs::write(dir.join("Cargo.toml"), m)?;
        write_deps_config(dir, s.crates, vendored)?;
        fs::write(dir.join("src/lib.rs"), s.lib_rs)?;
        fs::write(dir.join("src/bin/scratch.rs"), s.main_rs)
    };
    files().map_err(|e| RunnerError::io("write scratch project", e))
}

fn write_deps_config(dir: &Path, crates: &[String], vendored: bool) -> io::Result<()> {
    if !crates.is_empty() {
        fs::write(dir.join("Cargo.lock"), deps::lockfile())?;
        if vendored {
            fs::create_dir_all(dir.join(".cargo"))?;
            fs::write(dir.join(".cargo/config.toml"), deps::vendor_config())?;
        }
    }
    Ok(())
}

fn manifest_head() -> String {
    String::from(
        r#"[package]
name = "solution"
version = "0.1.0"
edition = "2021"
publish = false
autotests = false
autobins = false

# Stand-alone, even if the work directory sits inside another workspace.
[workspace]

[lib]
path = "src/lib.rs"
test = false
doctest = false
"#,
    )
}

fn manifest(with_hidden: bool, deps: &str) -> String {
    let mut m = String::from(
        r#"[package]
name = "solution"
version = "0.1.0"
edition = "2021"
publish = false
autotests = false

# Stand-alone, even if the work directory sits inside another workspace.
[workspace]

[lib]
path = "src/lib.rs"
test = false
doctest = false

[[test]]
name = "visible"
path = "tests/visible.rs"
"#,
    );
    if with_hidden {
        m.push_str(
            r#"
[[test]]
name = "hidden"
path = "tests/hidden.rs"
"#,
        );
    }
    if !deps.is_empty() {
        m.push_str("\n[dependencies]\n");
        m.push_str(deps);
    }
    m
}
