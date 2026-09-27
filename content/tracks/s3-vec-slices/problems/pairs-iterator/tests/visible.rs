use solution::*;

#[test]
fn odd_length() {
    check!(r#"v = [1, 2, 3, 4, 5]"#, pairs(&[1, 2, 3, 4, 5]).map(|(a, b)| (*a, *b)).collect::<Vec<_>>(), vec![(1, 2), (3, 4)]);
}

#[test]
fn items_outlive_iterator() {
    let v = ["a", "b"];
    let first = { let mut it = pairs(&v); it.next().unwrap() };
    check!(r#"v = ["a", "b"]"#, first, (&"a", &"b"));
}
