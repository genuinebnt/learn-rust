use solution::*;

#[test]
fn every_third() {
    check!(r#"(1..=10).every_nth(3)"#, (1..=10).every_nth(3).collect::<Vec<_>>(), vec![1, 4, 7, 10]);
}

#[test]
fn dedup_chars() {
    check!(r#""aabbbca".chars().dedup_adjacent()"#, "aabbbca".chars().dedup_adjacent().collect::<String>(), "abca");
}

#[test]
fn counts_words() {
    let mut sorted: Vec<_> = "a b a c a".split(' ').counts().into_iter().collect();
    sorted.sort();
    check!(r#""a b a c a".split(' ').counts(), sorted"#, sorted, vec![("a", 3), ("b", 1), ("c", 1)]);
}

#[test]
fn huge_skips() {
    check!(r#"(0u64..).every_nth(1_000_000_000_000).take(3)"#, (0u64..).every_nth(1_000_000_000_000).take(3).collect::<Vec<_>>(), vec![0, 1_000_000_000_000, 2_000_000_000_000]);
}

#[test]
fn exact_size_hint() {
    check!(r#"(0..10).every_nth(3).size_hint()"#, (0..10).every_nth(3).size_hint(), (4, Some(4)));
}

#[test]
fn on_references() {
    let v = ["x", "y", "z"];
    check!(r#"v.iter().every_nth(2) over ["x", "y", "z"]"#, v.iter().every_nth(2).collect::<Vec<_>>(), vec![&"x", &"z"]);
}
