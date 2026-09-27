use solution::*;

#[test]
fn exactly_22_inline() {
    let a = SmallStr::new(&"x".repeat(22));
    let b = SmallStr::new(&"x".repeat(23));
    check!(r#"22 and 23 ASCII bytes"#, (a.is_inline(), b.is_inline(), a.len(), b.len()), (true, false, 22, 23));
}

#[test]
fn multibyte_counts_bytes() {
    let a = SmallStr::new(&"é".repeat(11));
    let b = SmallStr::new(&"中".repeat(8));
    check!(r#"11 × 'é' (22 bytes), 8 × '中' (24 bytes)"#, (a.is_inline(), a.as_str().chars().count(), b.is_inline(), b.as_str()), (true, 11, false, "中中中中中中中中"));
}

#[test]
fn empty() {
    let (s, n) = anneal_prelude::allocs(|| SmallStr::new(""));
    check!(r#"SmallStr::new("")"#, (s.as_str(), s.is_inline(), s.is_empty(), n.count), ("", true, true, 0));
}

#[test]
fn clone_costs() {
    let x = SmallStr::new("tag");
    let y = SmallStr::new("a string that is far too long to fit");
    let (x2, a) = anneal_prelude::allocs(|| x.clone());
    let (y2, b) = anneal_prelude::allocs(|| y.clone());
    check!(r#"clone an inline and a heap SmallStr: allocations"#, (a.count, b.count, x2 == x, y2 == y), (0, 1, true, true));
}

#[test]
fn column_of_short_values() {
    let (col, n) = anneal_prelude::allocs(|| (0..1000).map(|i| SmallStr::new(if i < 999 { "US" } else { "c999" })).collect::<Vec<_>>());
    check!(r#"collect 1000 short SmallStrs into a Vec: allocations"#, (n.count, col.len(), col[999].as_str()), (1, 1000, "c999"));
}

#[test]
fn order_matches_str() {
    let mut v: Vec<SmallStr> = ["b", "ab", "a-very-long-string-indeed-yes", "B", ""].iter().map(|&s| SmallStr::new(s)).collect();
    v.sort();
    check!(r#"sort ["b", "ab", "a-very-long-string-indeed-yes", "B", ""]"#, v.iter().map(|s| s.as_str()).collect::<Vec<_>>(), vec!["", "B", "a-very-long-string-indeed-yes", "ab", "b"]);
}

#[test]
fn deref_to_str_methods() {
    let s = SmallStr::new("Hello");
    check!(r#"SmallStr::new("Hello"): to_uppercase, starts_with, len"#, (s.to_uppercase(), s.starts_with("He"), s.len()), ("HELLO".to_string(), true, 5));
}

fn hash_of<T: std::hash::Hash + ?Sized>(x: &T) -> u64 {
    use std::hash::{BuildHasher, BuildHasherDefault};
    BuildHasherDefault::<std::collections::hash_map::DefaultHasher>::default().hash_one(x)
}

#[test]
fn hash_matches_str() {
    check!(r#"hash of SmallStr vs &str, inline and heap"#, hash_of(&SmallStr::new("DE")) == hash_of("DE") && hash_of(&SmallStr::new("x-long-enough-to-live-on-the-heap")) == hash_of("x-long-enough-to-live-on-the-heap"), true);
}

#[test]
fn display_pads() {
    check!(r#"format!("[{:>5}]", SmallStr::new("ab"))"#, format!("[{:>5}]", SmallStr::new("ab")), "[   ab]");
}

#[test]
fn random_vs_string() {
    let mut rng = anneal_prelude::Rng::new(8207);
    let mut made = Vec::new();
    for _ in 0..300 {
        let n = if rng.bool() { rng.below(24) } else { rng.below(40) };
        let s = rng.string(n, "abcXYZ09 _éß中😀");
        let (small, a) = anneal_prelude::allocs(|| SmallStr::new(&s));
        let heap = s.len() > SmallStr::INLINE_CAP;
        check!(format!("SmallStr::new({s:?}): as_str, len, is_inline, allocations"), (small.as_str(), small.len(), small.is_inline(), a.count),
               (s.as_str(), s.len(), !heap, heap as u64));
        check!(format!("hash of SmallStr::new({s:?}) vs the str's"), hash_of(&small), hash_of(s.as_str()));
        made.push((small, s));
    }
    for _ in 0..300 {
        let (x, xs) = rng.pick(&made);
        let (y, ys) = rng.pick(&made);
        check!(format!("{xs:?} vs {ys:?}: ==, cmp"), (x == y, x.cmp(y)), (xs == ys, xs.cmp(ys)));
    }
}
