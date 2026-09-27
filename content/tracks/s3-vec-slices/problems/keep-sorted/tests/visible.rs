use solution::*;

#[test]
fn insert() {
    check!(r#"v = [1, 3, 5], x = 4"#, { let mut v = vec![1, 3, 5]; insert_sorted(&mut v, 4); v }, vec![1, 3, 4, 5]);
}

#[test]
fn count() {
    check!(r#"v = [1, 2, 2, 3, 7], lo = 2, hi = 3"#, count_in_range(&[1, 2, 2, 3, 7], 2, 3), 3);
}

#[test]
fn insert_duplicate() {
    check!(r#"v = [1, 2, 2, 3], x = 2"#, { let mut v = vec![1, 2, 2, 3]; insert_sorted(&mut v, 2); v }, vec![1, 2, 2, 2, 3]);
}

#[test]
fn count_none_inside() {
    check!(r#"v = [1, 5], lo = 2, hi = 4"#, count_in_range(&[1, 5], 2, 4), 0);
}

#[test]
fn count_bounds_inclusive() {
    check!(r#"v = [1, 2, 3], lo = 1, hi = 3"#, count_in_range(&[1, 2, 3], 1, 3), 3);
}
