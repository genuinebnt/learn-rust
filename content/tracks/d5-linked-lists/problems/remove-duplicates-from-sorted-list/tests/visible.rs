use solution::*;

#[test]
fn pairs() {
    check!(r#"[1,1,2,3,3]"#, values(&dedup_sorted(list(&[1, 1, 2, 3, 3]))), vec![1, 2, 3]);
}

#[test]
fn none() {
    check!(r#"[1,2]"#, values(&dedup_sorted(list(&[1, 2]))), vec![1, 2]);
}

#[test]
fn one_pair() {
    check!(r#"[1,1,2]"#, values(&dedup_sorted(list(&[1, 1, 2]))), vec![1, 2]);
}

#[test]
fn empty() {
    check!(r#"[]"#, dedup_sorted(None), None);
}

#[test]
fn all_same() {
    check!(r#"[7,7,7,7]"#, values(&dedup_sorted(list(&[7, 7, 7, 7]))), vec![7]);
}
