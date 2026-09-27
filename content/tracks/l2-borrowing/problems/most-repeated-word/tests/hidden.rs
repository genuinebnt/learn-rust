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
fn only_separators() {
    check!(r#"text = "  ,,; - ", k = 2"#, top_words("  ,,; - ", 2), Vec::<(&str, usize)>::new());
}

#[test]
fn digits_are_word_chars() {
    check!(r#"text = "v2 V2 route66", k = 2"#, top_words("v2 V2 route66", 2), vec![("v2", 2), ("route66", 1)]);
}

#[test]
fn apostrophe_splits() {
    check!(r#"text = "don't DON'T", k = 3"#, top_words("don't DON'T", 3), vec![("don", 2), ("t", 2)]);
}

#[test]
fn unicode_letters() {
    check!(r#"text = "café Café CAFÉ", k = 3"#, top_words("café Café CAFÉ", 3), vec![("café", 2), ("CAFÉ", 1)]);
}

#[test]
fn non_ascii_separator() {
    check!(r#"text = "a—b—a", k = 2"#, top_words("a—b—a", 2), vec![("a", 2), ("b", 1)]);
}

#[test]
fn newlines_and_tabs() {
    check!(r#"text = "one\ttwo\nTWO\n\none", k = 1"#, top_words("one\ttwo\nTWO\n\none", 1), vec![("one", 2)]);
}

#[test]
fn later_word_overtakes() {
    check!(r#"text = "a b b", k = 1"#, top_words("a b b", 1), vec![("b", 2)]);
}

#[test]
fn single_word() {
    check!(r#"text = "Solo", k = 1"#, top_words("Solo", 1), vec![("Solo", 1)]);
}

#[test]
fn words_borrow_the_text() {
    let text = String::from("Beta alpha BETA");
    let got = top_words(&text, 2);
    let range = text.as_bytes().as_ptr_range();
    check!("\"Beta alpha BETA\": every word points into the text", got.iter().all(|(w, _)| range.contains(&w.as_ptr())), true);
    check!("\"Beta alpha BETA\": and is the first spelling", got[0].0.as_ptr() == text.as_ptr(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6204);
    for _ in 0..300 {
        let len = rng.below(24);
        let text = rng.string(len, "aAbB c.");
        let k = rng.below(5);
        let words: Vec<&str> = text.split(|c: char| !c.is_alphanumeric()).filter(|w| !w.is_empty()).collect();
        // (lowercase, first spelling, count, first index)
        let mut seen: Vec<(String, &str, usize, usize)> = Vec::new();
        for (i, w) in words.iter().enumerate() {
            let low = w.to_ascii_lowercase();
            match seen.iter_mut().find(|s| s.0 == low) {
                Some(s) => s.2 += 1,
                None => seen.push((low, w, 1, i)),
            }
        }
        seen.sort_by(|a, b| b.2.cmp(&a.2).then(a.3.cmp(&b.3)));
        let want: Vec<(&str, usize)> = seen.iter().take(k).map(|s| (s.1, s.2)).collect();
        check!(format!("text = {text:?}, k = {k}"), top_words(&text, k), want);
    }
}

#[test]
fn long_text_allocates_per_distinct_word() {
    let spellings = ["Rust", "rust", "RUST", "go", "Go", "zig"];
    let mut text = String::new();
    for i in 0..200_000 {
        text.push_str(spellings[i % 6]);
        text.push(' ');
    }
    let (got, n) = allocs(|| top_words(&text, 3));
    check!("200000 words, 6 spellings of 3 words", got, vec![("Rust", 100_001), ("go", 66_666), ("zig", 33_333)]);
    check!("200000 words: at most 64 allocations (a String per word would be 200000)", n <= 64, true);
}
