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
fn slug_uppercase_is_owned() {
    check!(r#"slug("ABC") is owned"#, matches!(slug("ABC"), std::borrow::Cow::Owned(_)), true);
}

#[test]
fn slug_unicode() {
    check!(r#"slug("Ünïcode Straße")"#, slug("Ünïcode Straße"), "ünïcode-straße");
}

#[test]
fn slug_non_ascii_uppercase() {
    check!(r#"slug("Ünï")"#, slug("Ünï"), "ünï");
}

#[test]
fn slug_tabs_newlines() {
    check!(r#"slug("a\tb\nc")"#, slug("a\tb\nc"), "a-b-c");
}

#[test]
fn slug_leading_space_is_owned() {
    check!(r#"slug(" a")"#, (slug(" a").clone(), matches!(slug(" a"), std::borrow::Cow::Owned(_))), (std::borrow::Cow::<str>::Borrowed("a"), true));
}

#[test]
fn no_slash() {
    let paths = ["plain", "a/bc"].map(String::from);
    check!(r#"["plain", "a/bc"]"#, longest_file_name(&paths), Some("plain"));
}

#[test]
fn trailing_slash() {
    let paths = ["dir/", "a/b"].map(String::from);
    check!(r#"["dir/", "a/b"]"#, longest_file_name(&paths), Some("b"));
}

#[test]
fn clean_lines_crlf() {
    check!(r#"clean_lines("x\r\ny\r\n")"#, clean_lines("x\r\ny\r\n"), vec!["x", "y"]);
}

#[test]
fn results_borrow_the_input() {
    let text = String::from("  q\n");
    check!(r#"clean_lines points into the text"#, clean_lines(&text)[0].as_ptr() == text[2..].as_ptr(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6302);
    for _ in 0..300 {
        let len = rng.below(10);
        let text = rng.string(len, "aB -\n/");
        let want_slug = text.split_whitespace().collect::<Vec<_>>().join("-").to_lowercase();
        check!(format!("slug({text:?})"), slug(&text).into_owned(), want_slug.clone());
        check!(format!("slug({text:?}) borrows iff unchanged"), matches!(slug(&text), std::borrow::Cow::Borrowed(_)), want_slug == text);
        let want_lines: Vec<&str> = text.lines().map(str::trim).filter(|l| !l.is_empty()).collect();
        check!(format!("clean_lines({text:?})"), clean_lines(&text), want_lines.clone());
        let paths: Vec<String> = want_lines.iter().map(|l| l.to_string()).collect();
        let mut best: Option<&str> = None;
        for p in &paths {
            let n = p.rsplit('/').next().unwrap();
            if best.map_or(true, |b| n.len() > b.len()) {
                best = Some(n);
            }
        }
        check!(format!("longest_file_name({paths:?})"), longest_file_name(&paths), best);
    }
}

#[test]
fn unchanged_slug_does_not_allocate() {
    let text = "already-lowercase-".repeat(10_000);
    let (s, n) = allocs(|| slug(&text).len());
    check!("slug of a 180000-byte slug: allocations", (s, n), (180_000, 0));
}
