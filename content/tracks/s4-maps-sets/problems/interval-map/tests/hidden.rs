use solution::*;

#[test]
fn touching_allowed() {
    check!(r#"[0, 10) then [10, 20)"#, { let mut m = IntervalMap::new(); m.insert(0, 10, 1).unwrap(); (m.insert(10, 20, 2), m.get(10).copied()) }, (Ok(()), Some(2)));
}

#[test]
fn contains_existing() {
    check!(r#"[5, 6) then [0, 100)"#, { let mut m = IntervalMap::new(); m.insert(5, 6, 1).unwrap(); m.insert(0, 100, 2) }, Err(2));
}

#[test]
fn empty_interval() {
    check!(r#"[3, 3)"#, IntervalMap::new().insert(3, 3, 'x'), Err('x'));
}
