use solution::*;

#[test]
fn lookup() {
    check!(r#"[0, 10) → "a", [20, 30) → "b""#, { let mut m = IntervalMap::new(); m.insert(0, 10, "a").unwrap(); m.insert(20, 30, "b").unwrap(); (m.get(5).copied(), m.get(10).copied(), m.get(25).copied()) }, (Some("a"), None, Some("b")));
}

#[test]
fn overlap_refused() {
    check!(r#"[0, 10) then [5, 15)"#, { let mut m = IntervalMap::new(); m.insert(0, 10, "a").unwrap(); m.insert(5, 15, "b") }, Err("b"));
}

#[test]
fn touching_allowed() {
    check!(r#"[0, 10) then [10, 20)"#, { let mut m = IntervalMap::new(); m.insert(0, 10, 1).unwrap(); (m.insert(10, 20, 2), m.get(10).copied()) }, (Ok(()), Some(2)));
}

#[test]
fn empty_interval() {
    check!(r#"[3, 3)"#, IntervalMap::new().insert(3, 3, 'x'), Err('x'));
}

#[test]
fn get_on_empty() {
    check!(r#"no intervals; get(0)"#, IntervalMap::<u8>::new().get(0).copied(), None);
}
