use solution::*;

#[test]
fn middle() {
    check!(r#"[1,2,3,4,5], n = 2"#, values(&remove_nth_from_end(list(&[1, 2, 3, 4, 5]), 2)), vec![1, 2, 3, 5]);
}

#[test]
fn only() {
    check!(r#"[1], n = 1"#, remove_nth_from_end(list(&[1]), 1), None);
}
