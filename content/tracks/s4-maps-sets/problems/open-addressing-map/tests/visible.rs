use solution::*;

#[test]
fn insert_get() {
    check!(r#"insert 1 → "a", 2 → "b""#, { let mut m = OpenMap::new(); m.insert(1, "a"); m.insert(2, "b"); (m.get(1).copied(), m.get(3).copied(), m.len()) }, (Some("a"), None, 2));
}

#[test]
fn replace() {
    check!(r#"insert 7 → 1 then 7 → 2"#, { let mut m = OpenMap::new(); let first = m.insert(7, 1); let second = m.insert(7, 2); (first, second, m.get(7).copied(), m.len()) }, (None, Some(1), Some(2), 1));
}

#[test]
fn remove() {
    check!(r#"insert 5, remove 5"#, { let mut m = OpenMap::new(); m.insert(5, 'x'); (m.remove(5), m.get(5).copied(), m.remove(5), m.len()) }, (Some('x'), None, None, 0));
}
