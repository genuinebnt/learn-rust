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

#[test]
fn even_length() {
    check!(r#"v = [1, 2, 3, 4]"#, pairs(&[1, 2, 3, 4]).map(|(a, b)| (*a, *b)).collect::<Vec<_>>(), vec![(1, 2), (3, 4)]);
}

#[test]
fn single() {
    check!(r#"v = [1]"#, pairs(&[1]).count(), 0);
}

#[test]
fn len_of_five() {
    check!(r#"v = [1, 2, 3, 4, 5]"#, pairs(&[1, 2, 3, 4, 5]).len(), 2);
}
