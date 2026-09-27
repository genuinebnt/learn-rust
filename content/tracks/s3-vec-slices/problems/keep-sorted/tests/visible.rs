use solution::*;

#[test]
fn insert() {
    check!(r#"v = [1, 3, 5], x = 4"#, { let mut v = vec![1, 3, 5]; insert_sorted(&mut v, 4); v }, vec![1, 3, 4, 5]);
}

#[test]
fn count() {
    check!(r#"v = [1, 2, 2, 3, 7], lo = 2, hi = 3"#, count_in_range(&[1, 2, 2, 3, 7], 2, 3), 3);
}
