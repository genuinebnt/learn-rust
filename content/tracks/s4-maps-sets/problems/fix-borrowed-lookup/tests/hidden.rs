use solution::*;

#[test]
fn empty_name() {
    check!(r#"names = [""], id("")"#, Registry::new(&[""]).id(""), Some(0));
}

#[test]
fn later_duplicate_wins() {
    check!(r#"names = ["a", "a"], id("a")"#, Registry::new(&["a", "a"]).id("a"), Some(1));
}

#[test]
fn unicode() {
    check!(r#"names = ["x", "日本"], id("日本")"#, Registry::new(&["x", "日本"]).id("日本"), Some(1));
}

#[test]
fn prefix_is_not_a_match() {
    check!(r#"names = ["abc"], id("ab")"#, Registry::new(&["abc"]).id("ab"), None);
}

#[test]
fn trailing_space() {
    check!(r#"names = ["a"], id("a ")"#, Registry::new(&["a"]).id("a "), None);
}

#[test]
fn many() {
    check!(r#"10000 names, id("n9999")"#, { let ws: Vec<String> = (0..10_000).map(|i| format!("n{i}")).collect(); let refs: Vec<&str> = ws.iter().map(|w| w.as_str()).collect(); Registry::new(&refs).id("n9999") }, Some(9999));
}

use std::alloc::{GlobalAlloc, Layout, System};
use std::cell::Cell;

// Counts allocations made on the current thread, so the test below can check `id` makes none.
struct CountingAlloc;

thread_local! {
    static ALLOCS: Cell<usize> = const { Cell::new(0) };
}

unsafe impl GlobalAlloc for CountingAlloc {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let _ = ALLOCS.try_with(|n| n.set(n.get() + 1));
        unsafe { System.alloc(layout) }
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        unsafe { System.dealloc(ptr, layout) }
    }
}

#[global_allocator]
static GLOBAL: CountingAlloc = CountingAlloc;

#[test]
fn lookups_do_not_allocate() {
    let r = Registry::new(&["alpha", "beta"]);
    let before = ALLOCS.with(|n| n.get());
    let mut answered = 0;
    for _ in 0..1000 {
        if r.id("beta") == Some(1) {
            answered += 1;
        }
        if r.id("gamma").is_none() {
            answered += 1;
        }
    }
    let allocations = ALLOCS.with(|n| n.get()) - before;
    check!("1000 × id(\"beta\") and id(\"gamma\"); count allocations", (answered, allocations), (2000, 0));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(4007);
    for _ in 0..300 {
        let n = rng.below(6);
        let names: Vec<String> = (0..n).map(|_| { let l = rng.below(3); rng.string(l, "ab") }).collect();
        let refs: Vec<&str> = names.iter().map(|w| w.as_str()).collect();
        let r = Registry::new(&refs);
        let l = rng.below(3);
        let q = rng.string(l, "ab");
        let want = refs.iter().rposition(|&w| w == q).map(|i| i as u32);
        check!(format!("names = {refs:?}, id({q:?})"), r.id(&q), want);
    }
}

#[test]
fn scale_200k_lookups() {
    let ws: Vec<String> = (0..200_000).map(|i| format!("n{i}")).collect();
    let refs: Vec<&str> = ws.iter().map(|w| w.as_str()).collect();
    let r = Registry::new(&refs);
    let total: u64 = refs.iter().rev().map(|&w| u64::from(r.id(w).unwrap_or(0))).sum();
    check!("200000 names, look each one up", total, 19_999_900_000);
}
