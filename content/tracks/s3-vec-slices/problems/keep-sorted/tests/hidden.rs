use solution::*;

#[test]
fn insert_front_and_back() {
    check!(r#"v = [5], x = 1 then 9"#, { let mut v = vec![5]; insert_sorted(&mut v, 1); insert_sorted(&mut v, 9); v }, vec![1, 5, 9]);
}

#[test]
fn empty_range() {
    check!(r#"v = [1, 2, 3], lo = 5, hi = 1"#, count_in_range(&[1, 2, 3], 5, 1), 0);
}
