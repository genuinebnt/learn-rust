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

/// Always in the prelude: timing for `[perf] release = true` problems. `median_time` works anywhere;
/// `assert_faster` refuses to run in a debug build, where timings mean nothing.
const PRELUDE_TIMING: &str = r#"
/// Median wall time of `runs` calls to `f`, after one warm-up call. Results go through `black_box`, so the
/// optimizer can't delete the work being timed.
#[allow(dead_code)]
pub fn median_time<R>(runs: usize, mut f: impl FnMut() -> R) -> std::time::Duration {
    assert!(runs > 0, "median_time needs at least one run");
    std::hint::black_box(f());
    let mut times: Vec<std::time::Duration> = (0..runs)
        .map(|_| {
            let start = std::time::Instant::now();
            std::hint::black_box(f());
            start.elapsed()
        })
        .collect();
    times.sort();
    times[runs / 2]
}

/// Passes when `yours` runs at least `factor` times faster than `baseline`. Both are timed alternately
/// (`runs` times each, medians compared), so a slow patch on the machine hits both.
#[allow(dead_code)]
pub fn assert_faster<A, B>(what: &str, factor: f64, runs: usize, mut baseline: impl FnMut() -> A, mut yours: impl FnMut() -> B) {
    assert!(!cfg!(debug_assertions), "assert_faster needs [perf] release = true: debug-build timings mean nothing");
    assert!(runs > 0, "assert_faster needs at least one run");
    std::hint::black_box(baseline());
    std::hint::black_box(yours());
    let (mut base, mut mine) = (Vec::with_capacity(runs), Vec::with_capacity(runs));
    for _ in 0..runs {
        let start = std::time::Instant::now();
        std::hint::black_box(baseline());
        base.push(start.elapsed());
        let start = std::time::Instant::now();
        std::hint::black_box(yours());
        mine.push(start.elapsed());
    }
    base.sort();
    mine.sort();
    let (base, mine) = (base[runs / 2], mine[runs / 2]);
    let ratio = base.as_secs_f64() / mine.as_secs_f64().max(1e-9);
    println!("perf: {what}: baseline {base:?}, yours {mine:?}, {ratio:.1}x faster (needs {factor}x)");
    if ratio < factor {
        println!(
            "ANNEAL {{\"input\":{},\"expected\":{},\"got\":{}}}",
            crate::anneal_prelude::json(what),
            crate::anneal_prelude::json(&format!("at least {factor}x faster than the baseline")),
            crate::anneal_prelude::json(&format!("{ratio:.1}x (baseline {base:?}, yours {mine:?})")),
        );
        panic!("{what}: {ratio:.1}x faster than the baseline, needs {factor}x");
    }
}
"#;

/// `[perf] count_allocs = true`: a global allocator that counts the current thread's allocations.
const PRELUDE_ALLOCS: &str = r#"
/// What `allocs` saw: allocations (reallocations included) and the bytes requested.
#[allow(dead_code)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Allocs {
    pub count: u64,
    pub bytes: u64,
}

/// Runs `f` and returns its result with the heap allocations it made on this thread. Work handed to
/// other threads isn't counted.
#[allow(dead_code)]
pub fn allocs<R>(f: impl FnOnce() -> R) -> (R, Allocs) {
    let before = counting::now();
    let r = f();
    let after = counting::now();
    (r, Allocs { count: after.0 - before.0, bytes: after.1 - before.1 })
}

mod counting {
    use std::alloc::{GlobalAlloc, Layout, System};
    use std::cell::Cell;

    thread_local! {
        static SEEN: Cell<(u64, u64)> = const { Cell::new((0, 0)) };
    }

    fn note(bytes: usize) {
        // `try_with`: allocations can happen while the thread's locals are being torn down.
        let _ = SEEN.try_with(|s| {
            let (n, b) = s.get();
            s.set((n + 1, b + bytes as u64));
        });
    }

    pub fn now() -> (u64, u64) {
        SEEN.with(|s| s.get())
    }

    struct Counting;

    #[allow(unused_unsafe)]
    unsafe impl GlobalAlloc for Counting {
        unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
            note(layout.size());
            unsafe { System.alloc(layout) }
        }
        unsafe fn alloc_zeroed(&self, layout: Layout) -> *mut u8 {
            note(layout.size());
            unsafe { System.alloc_zeroed(layout) }
        }
        unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
            note(new_size);
            unsafe { System.realloc(ptr, layout, new_size) }
        }
        unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
            unsafe { System.dealloc(ptr, layout) }
        }
    }

    #[global_allocator]
    static GLOBAL: Counting = Counting;
}
"#;

/// `[perf] asm = true`: the solution's release assembly, and helpers to read one function of it.
const PRELUDE_ASM: &str = r#"
/// The solution library's release assembly, compiled on its own in one codegen unit. Functions checked
/// here must be plain `pub fn`s (or methods): not generic and not `#[inline]`, or the compiler doesn't
/// emit them until a caller needs them.
#[allow(dead_code)]
pub mod asm {
    pub const ALL: &str = include_str!("solution.s");

    /// A symbol's first line: `name:`, possibly followed by an `# @name` comment.
    fn is_label(line: &str) -> bool {
        !line.starts_with(char::is_whitespace) && !line.starts_with('.') && line.split_whitespace().next().is_some_and(|w| w.ends_with(':'))
    }

    /// Whether a symbol names the solution's `path` ("total", or "Matrix::mul" for a method). Handles both
    /// manglings: legacy (`_ZN8solution5total17h<hash>E`) and v0 (`_RNvCs<hash>_8solution5total`), which
    /// rustc uses when `RUSTC_BOOTSTRAP` is set, as it is here. Every segment appears length-prefixed, in
    /// order, and the symbol ends with the last one.
    fn matches(label: &str, path: &str) -> bool {
        let mut sym = label.split_whitespace().next().unwrap_or("").trim_end_matches(':');
        if sym == path || sym.strip_prefix('_') == Some(path) {
            return true;
        }
        if let Some(i) = sym.rfind("17h").filter(|&i| sym.len() == i + 20 && sym.ends_with('E')) {
            sym = &sym[..i];
        }
        if !sym.contains("8solution") {
            return false;
        }
        let segs: Vec<String> = path.split("::").map(|s| format!("{}{s}", s.len())).collect();
        let mut rest = sym;
        for s in &segs {
            match rest.find(s.as_str()) {
                Some(i) => rest = &rest[i + s.len()..],
                None => return false,
            }
        }
        rest.is_empty()
    }

    /// The instructions of the solution's function `name` ("sum_rows", or "Matrix::mul" for a method).
    /// Panics listing the functions it found when there's no such function.
    pub fn function(name: &str) -> String {
        let mut lines = ALL.lines().skip_while(|l| !(is_label(l) && matches(l, name)));
        let Some(_) = lines.next() else {
            panic!("no function {name:?} in the release assembly; found: {:?}", functions());
        };
        lines
            .take_while(|l| !l.contains("func_end") && l.trim() != ".cfi_endproc")
            .filter(|l| !is_label(l))
            .collect::<Vec<_>>()
            .join("
")
    }

    /// The solution's functions in the assembly, as mangled symbols.
    pub fn functions() -> Vec<&'static str> {
        ALL.lines()
            .filter(|l| is_label(l) && l.contains("8solution"))
            .filter_map(|l| l.split_whitespace().next())
            .map(|w| w.trim_end_matches(':'))
            .collect()
    }

    /// Instruction lines only: no directives, labels or comments.
    pub fn instructions(body: &str) -> Vec<&str> {
        body.lines()
            .map(str::trim)
            .filter(|l| !l.is_empty() && !l.starts_with('.') && !l.starts_with('#') && !l.starts_with("//") && !l.starts_with(';'))
            .collect()
    }

    /// Whether `body` calls or jumps to a symbol containing `callee`, e.g. "panic_bounds_check".
    pub fn calls(body: &str, callee: &str) -> bool {
        instructions(body).iter().any(|l| l.contains(callee))
    }

    /// Whether `body` uses SIMD (packed vector) instructions: xmm/ymm/zmm packed ops on x86_64, NEON
    /// lane arrangements (`v0.4s`, `v1.16b`, ...) on aarch64.
    pub fn uses_simd(body: &str) -> bool {
        const X86: [&str; 12] = ["ymm", "zmm", "padd", "psub", "pmul", "pcmp", "pmovmsk", "pand", "por", "pxor", "addp", "mulp"];
        const ARM: [&str; 8] = [".16b", ".8b", ".8h", ".4h", ".4s", ".2s", ".2d", ".1d"];
        instructions(body).iter().any(|l| X86.iter().chain(ARM.iter()).any(|p| l.contains(p)))
    }
}
"#;

/// The file `[perf] asm = true` writes the library's assembly to, relative to the package root.
pub(crate) const ASM_EMIT: &str = "asm=tests/anneal/solution.s";

/// The test prelude for `perf`: `check!` and `Rng` always, the measuring helpers `perf` asks for.
fn prelude(perf: crate::Perf) -> String {
    let mut p = String::from(PRELUDE);
    p.push_str(PRELUDE_TIMING);
    if perf.count_allocs {
        p.push_str(PRELUDE_ALLOCS);
    }
    if perf.asm {
        p.push_str(PRELUDE_ASM);
    }
    p
}

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
    fs::write(dir.join("tests/anneal/prelude.rs"), prelude(sub.perf))?;
    if sub.perf.asm {
        // Replaced by the real assembly before the tests build; an empty file keeps `include_str!` valid.
        fs::write(dir.join("tests/anneal/solution.s"), "")?;
    }
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
