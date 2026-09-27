use solution::*;

#[test]
fn middle() {
    check!(r#"[1,2,3,4,5], n = 2"#, values(&remove_nth_from_end(list(&[1, 2, 3, 4, 5]), 2)), vec![1, 2, 3, 5]);
}

#[test]
fn only() {
    check!(r#"[1], n = 1"#, remove_nth_from_end(list(&[1]), 1), None);
}

#[test]
fn last() {
    check!(r#"[1,2], n = 1"#, values(&remove_nth_from_end(list(&[1, 2]), 1)), vec![1]);
}

#[test]
fn first() {
    check!(r#"[1,2], n = 2"#, values(&remove_nth_from_end(list(&[1, 2]), 2)), vec![2]);
}

#[test]
fn out_of_range() {
    check!(r#"[1,2], n = 3 and 0"#, (values(&remove_nth_from_end(list(&[1, 2]), 3)), values(&remove_nth_from_end(list(&[1, 2]), 0))), (vec![1, 2], vec![1, 2]));
}
