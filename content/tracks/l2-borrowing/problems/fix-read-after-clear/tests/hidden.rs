use solution::*;

use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::Cell;

struct CountingAlloc;

thread_local! {
    static ALLOCS: Cell<usize> = const { Cell::new(0) };
}

unsafe impl GlobalAlloc for CountingAlloc {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let _ = ALLOCS.try_with(|n| n.set(n.get() + 1));
        unsafe { System.alloc(layout) }
    }

    unsafe fn realloc(&self, ptr: *mut u8, layout: Layout, new_size: usize) -> *mut u8 {
        let _ = ALLOCS.try_with(|n| n.set(n.get() + 1));
        unsafe { System.realloc(ptr, layout, new_size) }
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        unsafe { System.dealloc(ptr, layout) }
    }
}

#[global_allocator]
static GLOBAL: CountingAlloc = CountingAlloc;

/// Runs `f` and returns its result with the number of allocations (and reallocations) it made.
fn allocs<R>(f: impl FnOnce() -> R) -> (R, usize) {
    let before = ALLOCS.with(|n| n.get());
    let r = f();
    (r, ALLOCS.with(|n| n.get()) - before)
}

#[test]
fn empty_lines() {
    check!(r#"input "\n\na\n""#, key_runs("\n\na\n".as_bytes()).unwrap(), vec![("".to_string(), 2), ("a".to_string(), 1)]);
}

#[test]
fn empty_key() {
    check!(r#"input ":x\n:y\nz\n""#, key_runs(":x\n:y\nz\n".as_bytes()).unwrap(), vec![("".to_string(), 2), ("z".to_string(), 1)]);
}

#[test]
fn key_equals_line() {
    check!(r#"input "a\na:1\n""#, key_runs("a\na:1\n".as_bytes()).unwrap(), vec![("a".to_string(), 2)]);
}

#[test]
fn single_line() {
    check!(r#"input "only""#, key_runs("only".as_bytes()).unwrap(), vec![("only".to_string(), 1)]);
}

#[test]
fn alternating() {
    check!(r#"input "a\nb\na\nb\n""#, key_runs("a\nb\na\nb\n".as_bytes()).unwrap(), vec![("a".to_string(), 1), ("b".to_string(), 1), ("a".to_string(), 1), ("b".to_string(), 1)]);
}

#[test]
fn unicode_keys() {
    check!(r#"input "日本:1\n日本:2\né\n""#, key_runs("日本:1\n日本:2\né\n".as_bytes()).unwrap(), vec![("日本".to_string(), 2), ("é".to_string(), 1)]);
}

#[test]
fn spaces_are_kept() {
    check!(r#"input " a:1\na:2\n""#, key_runs(" a:1\na:2\n".as_bytes()).unwrap(), vec![(" a".to_string(), 1), ("a".to_string(), 1)]);
}

#[test]
fn lone_cr_kept_inside() {
    check!(r#"input "a\rb\n""#, key_runs("a\rb\n".as_bytes()).unwrap(), vec![("a\rb".to_string(), 1)]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6209);
    for _ in 0..300 {
        let n = rng.below(8);
        let mut text = String::new();
        for _ in 0..n {
            let len = rng.below(4);
            text.push_str(&rng.string(len, "ab:"));
            text.push('\n');
        }
        let mut want: Vec<(String, usize)> = Vec::new();
        for line in text.lines() {
            let key = line.split(':').next().unwrap();
            match want.last_mut() {
                Some((k, c)) if k == key => *c += 1,
                _ => want.push((key.to_string(), 1)),
            }
        }
        check!(format!("input {text:?}"), key_runs(text.as_bytes()).unwrap(), want);
    }
}

#[test]
fn allocates_per_run_not_per_line() {
    let mut text = String::new();
    for i in 0..200_000 {
        text.push_str(&format!("key{}:{i}\n", i / 200));
    }
    let (runs, n) = allocs(|| key_runs(text.as_bytes()).unwrap());
    check!("200000 lines in 1000 runs of 200", (runs.len(), runs[999].clone()), (1000, ("key999".to_string(), 200)));
    check!("200000 lines in 1000 runs: at most 1100 allocations (one per line would be 200000)", n <= 1100, true);
}
