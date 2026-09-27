use solution::*;

#[test]
fn lookup() {
    check!(r#"[0, 10) → "a", [20, 30) → "b""#, { let mut m = IntervalMap::new(); m.insert(0, 10, "a").unwrap(); m.insert(20, 30, "b").unwrap(); (m.get(5).copied(), m.get(10).copied(), m.get(25).copied()) }, (Some("a"), None, Some("b")));
}

#[test]
fn overlap_refused() {
    check!(r#"[0, 10) then [5, 15)"#, { let mut m = IntervalMap::new(); m.insert(0, 10, "a").unwrap(); m.insert(5, 15, "b") }, Err("b"));
}
