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
fn remove_unknown_doc() {
    let mut ix = Index::new();
    ix.add(1, "rust borrow check");
    ix.add(2, "rust rust lifetimes");
    ix.add(5, "borrow");
    check!(r#"add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow"; remove_doc(3)"#, (ix.remove_doc(3), ix.words()), (0, 4));
}

#[test]
fn remove_all_docs() {
    let mut ix = Index::new();
    ix.add(1, "rust borrow check");
    ix.add(2, "rust rust lifetimes");
    ix.add(5, "borrow");
    check!(r#"add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow"; remove_doc 1, 2, 5"#, (ix.remove_doc(1), ix.remove_doc(2), ix.remove_doc(5), ix.words()), (3, 2, 1, 0));
}

#[test]
fn empty_text() {
    let mut ix = Index::new();
    ix.add(1, "");
    ix.add(2, "   ");
    check!(r#"add 1 "", add 2 "   ""#, ix.words(), 0);
}

#[test]
fn case_sensitive() {
    let mut ix = Index::new();
    ix.add(1, "Rust rust");
    check!(r#"add 1 "Rust rust""#, (ix.docs("Rust"), ix.docs("rust"), ix.docs("RUST")), (&[1u32][..], &[1u32][..], &[][..]));
}

#[test]
fn tabs_and_newlines() {
    let mut ix = Index::new();
    ix.add(3, "a\tb\n a");
    check!(r#"add 3 "a\tb\n a""#, (ix.docs("a"), ix.docs("b")), (&[3u32][..], &[3u32][..]));
}

#[test]
fn hit_is_separate_from_docs() {
    let mut ix = Index::new();
    ix.add(1, "rust borrow check");
    ix.add(2, "rust rust lifetimes");
    ix.add(5, "borrow");
    check!(r#"add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow"; hit("rust")"#, (ix.hit("rust"), ix.docs("rust")), (1, &[1u32, 2][..]));
}

#[test]
fn docs_mut_existing_keeps_list() {
    let mut ix = Index::new();
    ix.add(1, "rust borrow check");
    ix.add(2, "rust rust lifetimes");
    ix.add(5, "borrow");
    check!(r#"add 1 "rust borrow check", 2 "rust rust lifetimes", 5 "borrow"; docs_mut("borrow") without editing"#, { ix.docs_mut("borrow"); (ix.docs("borrow"), ix.words()) }, (&[1u32, 5][..], 4));
}

#[test]
fn docs_mut_missing_then_empty() {
    let mut ix = Index::new();
    check!(r#"docs_mut("x") on a new index"#, { ix.docs_mut("x"); (ix.docs("x"), ix.words()) }, (&[][..], 1));
}

#[test]
fn unicode_words() {
    let mut ix = Index::new();
    ix.add(4, "日本 café 日本");
    check!(r#"add 4 "日本 café 日本""#, (ix.docs("日本"), ix.docs("café")), (&[4u32][..], &[4u32][..]));
}

#[test]
fn random_vs_model() {
    use std::collections::BTreeMap;
    let mut rng = anneal_prelude::Rng::new(6210);
    for _ in 0..200 {
        let mut ix = Index::new();
        let mut model: BTreeMap<String, Vec<u32>> = BTreeMap::new();
        let mut ops = Vec::new();
        let mut doc = 0;
        for _ in 0..8 {
            if rng.below(3) > 0 {
                doc += 1 + rng.below(2) as u32;
                let len = rng.below(8);
                let text = rng.string(len, "ab c");
                ix.add(doc, &text);
                for w in text.split_whitespace() {
                    let list = model.entry(w.to_string()).or_default();
                    if list.last() != Some(&doc) {
                        list.push(doc);
                    }
                }
                ops.push(format!("add {doc} {text:?}"));
            } else {
                let d = 1 + rng.below(doc as usize + 1) as u32;
                let mut changed = 0;
                model.retain(|_, list| {
                    if let Some(i) = list.iter().position(|&x| x == d) {
                        list.remove(i);
                        changed += 1;
                    }
                    !list.is_empty()
                });
                ops.push(format!("remove_doc {d}"));
                check!(ops.join(", "), ix.remove_doc(d), changed);
            }
        }
        check!(format!("{}; words()", ops.join(", ")), ix.words(), model.len());
        for w in ["a", "b", "ab", "ba", "c", "zz"] {
            let want: &[u32] = model.get(w).map_or(&[], |v| v.as_slice());
            check!(format!("{}; docs({w:?})", ops.join(", ")), ix.docs(w), want);
        }
    }
}

#[test]
fn known_words_do_not_allocate() {
    let mut ix = Index::new();
    let words = ["alpha", "beta", "gamma", "delta"];
    for w in words {
        ix.hit(w);
    }
    let (_, n) = allocs(|| {
        for i in 0..100_000 {
            ix.hit(words[i % 4]);
        }
    });
    check!("100000 hits on 4 known words: allocations", n, 0);
    check!("hits on alpha", ix.hit("alpha"), 25_002);
    let text = words.repeat(25_000).join(" ");
    ix.add(1, &text);
    let (_, n) = allocs(|| ix.add(2, &text));
    check!("add(2, 100000 words, 4 known): at most 16 allocations (a key per word would be 100000)", n <= 16, true);
    check!("docs(gamma)", ix.docs("gamma"), &[1u32, 2][..]);
}
