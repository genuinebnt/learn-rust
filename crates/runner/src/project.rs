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
///
/// `anneal_prelude::Rng`: a seeded splitmix64 generator with no crate dependency, for
/// randomized tests that compare against a brute-force reference written in the test.
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

/// Seeded splitmix64. The same seed gives the same sequence on every machine.
#[allow(dead_code)]
pub struct Rng(u64);

#[allow(dead_code)]
impl Rng {
    pub fn new(seed: u64) -> Self {
        Rng(seed)
    }

    pub fn next_u64(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }

    /// A value in `0..n`; `n` must be positive.
    pub fn below(&mut self, n: usize) -> usize {
        assert!(n > 0, "Rng::below(0)");
        (self.next_u64() % n as u64) as usize
    }

    /// A value in `lo..=hi`.
    pub fn int(&mut self, lo: i64, hi: i64) -> i64 {
        assert!(lo <= hi, "Rng::int({lo}, {hi})");
        let span = (hi as i128 - lo as i128 + 1) as u128;
        (lo as i128 + (self.next_u64() as u128 % span) as i128) as i64
    }

    /// `len` values in `lo..=hi`, converted to `T` (e.g. `i32`, `u8`).
    pub fn vec<T: TryFrom<i64>>(&mut self, len: usize, lo: i64, hi: i64) -> Vec<T> {
        (0..len).map(|_| T::try_from(self.int(lo, hi)).ok().expect("Rng::vec: value out of range for T")).collect()
    }

    pub fn bool(&mut self) -> bool {
        self.next_u64() & 1 == 1
    }

    /// A random element of a non-empty slice.
    pub fn pick<'a, T>(&mut self, xs: &'a [T]) -> &'a T {
        &xs[self.below(xs.len())]
    }

    /// Fisher–Yates.
    pub fn shuffle<T>(&mut self, xs: &mut [T]) {
        for i in (1..xs.len()).rev() {
            let j = self.below(i + 1);
            xs.swap(i, j);
        }
    }

    /// `len` chars drawn from `alphabet`.
    pub fn string(&mut self, len: usize, alphabet: &str) -> String {
        let cs: Vec<char> = alphabet.chars().collect();
        (0..len).map(|_| *self.pick(&cs)).collect()
    }
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
