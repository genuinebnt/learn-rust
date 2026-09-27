use solution::*;

#[test]
fn pairs() {
    check!(r#"[1,1,2,3,3]"#, values(&dedup_sorted(list(&[1, 1, 2, 3, 3]))), vec![1, 2, 3]);
}

#[test]
fn none() {
    check!(r#"[1,2]"#, values(&dedup_sorted(list(&[1, 2]))), vec![1, 2]);
}
