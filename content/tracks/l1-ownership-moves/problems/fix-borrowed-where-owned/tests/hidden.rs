use solution::*;

#[test]
fn empty_everything() {
    check!(r#"new("", [], Some(""))"#, Tag::new("", &[], Some("")), Tag { name: String::new(), aliases: vec![], note: Some(String::new()) });
}

#[test]
fn aliases_in_order() {
    check!(r#"aliases ["b", "a", "b"]"#, Tag::new("x", &["b", "a", "b"], None).aliases, vec!["b", "a", "b"]);
}

#[test]
fn spaces_and_case_kept() {
    check!(r#"new(" RuSt ", [" r "], Some(" N "))"#, Tag::new(" RuSt ", &[" r "], Some(" N ")), Tag { name: " RuSt ".to_string(), aliases: vec![" r ".to_string()], note: Some(" N ".to_string()) });
}

#[test]
fn unicode() {
    check!(r#"new("日本語", ["🦀"], None)"#, Tag::new("日本語", &["🦀"], None).name + &Tag::new("日本語", &["🦀"], None).aliases[0], "日本語🦀".to_string());
}

#[test]
fn source_changed_later() {
    check!(r#"input String changed after new"#, { let mut s = String::from("old"); let t = Tag::new(s.as_str(), &[], None); s.push_str("er"); (t.name, s) }, ("old".to_string(), "older".to_string()));
}

#[test]
fn owned_name_no_allocation() {
    let mut name = String::with_capacity(100);
    name.push_str("big");
    let (tag, n) = allocs(|| Tag::new(name, &[], None));
    check!(r#"new(String, [], None) makes no copy of the name"#, (n, tag.name.capacity()), (0, 100));
}

#[test]
fn literal_name_one_allocation() {
    check!(r#"new("lit", [], None) allocates once"#, allocs(|| Tag::new("lit", &[], None)).1, 1);
}

#[test]
fn two_tags_one_str() {
    check!(r#"two tags from the same &str don't share a buffer"#, { let s = "same"; let (a, b) = (Tag::new(s, &[], None), Tag::new(s, &[], None)); a == b && a.name.as_ptr() != b.name.as_ptr() }, true);
}

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

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        unsafe { System.dealloc(ptr, layout) }
    }
}

#[global_allocator]
static GLOBAL: CountingAlloc = CountingAlloc;

/// Runs `f` and returns its result with the number of allocations it made.
fn allocs<R>(f: impl FnOnce() -> R) -> (R, usize) {
    let before = ALLOCS.with(|n| n.get());
    let r = f();
    (r, ALLOCS.with(|n| n.get()) - before)
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6106);
    for _ in 0..300 {
        let len = rng.below(8);
        let name = rng.string(len, "aZ é日🦀");
        let k = rng.below(4);
        let aliases: Vec<String> = (0..k).map(|_| { let l = rng.below(4); rng.string(l, "ab ") }).collect();
        let note = if rng.bool() { let l = rng.below(4); Some(rng.string(l, "nö")) } else { None };
        let refs: Vec<&str> = aliases.iter().map(|a| a.as_str()).collect();
        let want = Tag { name: name.clone(), aliases: aliases.clone(), note: note.clone() };
        let input = format!("name = {name:?}, aliases = {aliases:?}, note = {note:?}");
        check!(input.clone(), Tag::new(name.as_str(), &refs, note.as_deref()), want);
        check!(format!("{input}, name owned"), Tag::new(name.clone(), &refs, note.as_deref()).name, name);
    }
}
